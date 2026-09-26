"""Managers for killboard."""

# Standard Library
import time
from typing import TYPE_CHECKING, Any

# Third Party
import requests

# Pydantic
from pydantic import ValidationError

# Django
from django.db import models, transaction

# Alliance Auth (External Libs)
from eve_sde.models import ItemType

# AA Killstats
from killstats.helpers.killmailbody import KillmailBody, zKBWebKillmail

if TYPE_CHECKING:
    # AA Killstats
    from killstats.models.killboard import Killmail as KillmailContext


# AA Killstats
from killstats import USER_AGENT_TEXT, __title__, app_settings
from killstats.providers import logger


class KillmailQueryCore(models.QuerySet):
    def filter_entities(self, entities):
        """Filter Kills and Losses from Entities List (Corporations or Alliances)."""
        # pylint: disable=import-outside-toplevel
        # AA Killstats
        from killstats.models.killboard import Attacker

        # Get all Killmail IDs
        km_ids = self.values_list("killmail_id", flat=True)

        # Get all Attackers and Victims from Entities
        attacker_kms_ids = Attacker.objects.filter(
            models.Q(corporation_id__in=entities)
            | models.Q(alliance_id__in=entities)
            | models.Q(character_id__in=entities),
            killmail_id__in=km_ids,
        ).values_list("killmail_id", flat=True)

        victim_kms_ids = self.filter(
            models.Q(victim_id__in=entities)
            | models.Q(victim_corporation_id__in=entities)
            | models.Q(victim_alliance_id__in=entities)
        ).values_list("killmail_id", flat=True)

        # Combine and deduplicate Killmail IDs
        combined_kms_ids = set(attacker_kms_ids).union(victim_kms_ids)

        return self.filter(killmail_id__in=combined_kms_ids)

    def filter_entities_kills(self, entities):
        """Filter Kills from Entities List (Corporations or Alliances)."""
        # pylint: disable=import-outside-toplevel
        # AA Killstats
        from killstats.models.killboard import Attacker

        kms = []

        # Sammle alle Angreifer-Daten
        km_ids = self.values_list("killmail_id", flat=True)

        kms_data = Attacker.objects.filter(
            models.Q(corporation_id__in=entities)
            | models.Q(alliance_id__in=entities)
            | models.Q(character_id__in=entities),
            killmail_id__in=km_ids,
        ).values_list("killmail_id", flat=True)

        for killmail_id in kms_data:
            kms.append(killmail_id)

        return self.filter(killmail_id__in=kms)

    def filter_entities_losses(self, entities):
        """Filter Losses from Entities List (Corporations or Alliances)."""
        kms = []

        victim_kms = self.filter(
            models.Q(victim_id__in=entities)
            | models.Q(victim_corporation_id__in=entities)
            | models.Q(victim_alliance_id__in=entities)
        ).values_list("killmail_id", flat=True)

        for killmail_id in victim_kms:
            kms.append(killmail_id)

        return self.filter(killmail_id__in=kms)

    def filter_structure(self, exclude=False):
        """Filter or Exclude Structure Kills."""
        if exclude:
            return self.exclude(victim_ship__group__category_id=65)
        return self.filter(victim_ship__group__category_id=65)

    def filter_threshold(self, threshold: int):
        """Filter Killmails are in Threshold."""
        return self.filter(victim_total_value__gt=threshold)


class KillmailQueryMining(KillmailQueryCore):
    def filter_barge(self):
        """Filter Mining Barge."""
        return self.filter(victim_ship__group_id=463)

    def filter_exhumer(self):
        """Filter Exhumer."""
        return self.filter(victim_ship__group_id=543)

    def filter_indu_command_ship(self):
        """Filter Industrial Command Ship."""
        return self.filter(victim_ship__group_id=941)

    def filter_capital_indu_ship(self):
        """Filter Capital Industrial Ship."""
        return self.filter(victim_ship__group_id=883)


class KillmailQuerySet(KillmailQueryMining):
    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            logger.debug("Returning all Squads for superuser %s.", user)
            return self

        if user.has_perm("killstats.admin_access"):
            logger.debug("Returning all Killboards for Admin %s.", user)
            return self

        return self.none()


class KillmailManager(models.Manager["KillmailContext"]):
    def get_queryset(self):
        return KillmailQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def filter_entities_kills(self, entities):
        return self.get_queryset().filter_entities_kills(entities)

    def filter_entities_losses(self, entities):
        return self.get_queryset().filter_entities_losses(entities)

    def filter_entities(self, entities):
        return self.get_queryset().filter_entities(entities)

    def filter_structure(self, exclude=False):
        return self.get_queryset().filter_structure(exclude=exclude)

    # pylint: disable=too-many-locals
    def check_missing_killmails(
        self,
        corporation_id: int | None = None,
        alliance_id: int | None = None,
        pages: int = 3,
        delay_between_pages: float = 1.0,
    ) -> list[KillmailBody]:
        """
        Fetch up to `pages` from zKillboard for corporation_id and/or alliance_id and compare against database.
        Pre-caches missing killmails as KillmailBody objects.

        Args:
            corporation_id: The ID of the corporation to fetch killmails for.
            alliance_id: The ID of the alliance to fetch killmails for.
            pages: The number of pages to fetch from zKillboard.
            delay_between_pages: The delay between fetching each page, in seconds.

        Returns:
            A list of KillmailBody objects representing the missing killmails.
        """
        if not corporation_id and not alliance_id:
            raise ValueError("Either corporation_id or alliance_id must be provided.")

        path_parts = []
        if corporation_id:
            path_parts.append(f"corporationID/{corporation_id}")
        if alliance_id:
            path_parts.append(f"allianceID/{alliance_id}")

        base_path = "/".join(path_parts) + "/"

        all_killmail_ids = set()
        killmail_bodies: dict[int, KillmailBody] = {}
        pages_fetched = 0
        headers = {"User-Agent": USER_AGENT_TEXT, "Content-Type": "application/json"}

        for page in range(1, max(1, pages) + 1):
            if page > 1 and delay_between_pages > 0:
                time.sleep(delay_between_pages)

            try:
                url = f"{app_settings.ZKILLBOARD_API_URL}{base_path}page/{page}/"
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                # Validate and parse the response JSON into a list of zKBWebKillmail objects.
                killmails: list[zKBWebKillmail] = []
                zkb_mails = response.json()
                for zkb_mail in zkb_mails:

                    killmails.append(zKBWebKillmail.model_validate(zkb_mail))
            except (ValidationError, requests.RequestException) as exc:
                logger.error(
                    "Error fetching zKillboard page %s in check_missing: %s",
                    page,
                    exc,
                    exc_info=True,
                )
                break

            for km in killmails:
                # Add the killmail ID to the set of all killmail IDs and store the raw killmail data by ID.
                all_killmail_ids.add(km.killmail_id)
                killmail_bodies[km.killmail_id] = km.convert_to_killmail_body()
            pages_fetched += 1

        # Determine which killmail IDs are already present in the database.
        existing_ids = set(
            self.filter(killmail_id__in=all_killmail_ids).values_list(
                "killmail_id", flat=True
            )
        )

        # Determine which killmail IDs are missing from the database.
        missing_ids = sorted(list(all_killmail_ids - existing_ids), reverse=True)
        return [killmail_bodies[km_id] for km_id in missing_ids]

    def create_from_killmail(self, killmail_body: KillmailBody):
        """create a new EveKillmail from a Killmail object and returns it"""
        # AA Killstats
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Killmail

        with transaction.atomic():
            attackers_list = []

            corporation_id = killmail_body.esi.victim.corporation_id
            region_id = killmail_body.get_region_id(killmail_body.esi.solar_system_id)
            victim_ship = ItemType.objects.get(id=killmail_body.esi.victim.ship_type_id)
            victim = None

            if killmail_body.esi.victim.character_id:
                victim = killmail_body.get_or_create_entity(
                    killmail_body.esi.victim.character_id
                )
            elif killmail_body.esi.victim.alliance_id:
                victim = killmail_body.get_or_create_entity(
                    killmail_body.esi.victim.alliance_id
                )
            elif killmail_body.esi.victim.corporation_id:
                victim = killmail_body.get_or_create_entity(
                    killmail_body.esi.victim.corporation_id
                )

            for attacker in killmail_body.esi.attackers:
                if attacker.character_id:
                    attackers_list.append(attacker.character_id)

            if attackers_list:
                try:
                    unique_attackers = list(set(attackers_list))
                    killmail_body.create_names_bulk(eve_ids=unique_attackers)
                # pylint: disable=broad-exception-caught
                except Exception as e:
                    logger.debug("Error on Create Names: %s", e, exc_info=True)

            km = Killmail.objects.create(
                killmail_id=killmail_body.esi.killmail_id,
                killmail_date=killmail_body.esi.killmail_time,
                victim=victim,
                victim_ship=victim_ship,
                victim_corporation_id=corporation_id,
                victim_alliance_id=killmail_body.esi.victim.alliance_id,
                hash=killmail_body.zkb.hash,
                victim_total_value=killmail_body.zkb.totalValue,
                victim_fitted_value=killmail_body.zkb.fittedValue,
                victim_destroyed_value=killmail_body.zkb.destroyedValue,
                victim_dropped_value=killmail_body.zkb.droppedValue,
                victim_region_id=region_id,
                victim_solar_system_id=killmail_body.esi.solar_system_id,
                victim_position_x=killmail_body.esi.victim.position.x,
                victim_position_y=killmail_body.esi.victim.position.y,
                victim_position_z=killmail_body.esi.victim.position.z,
            )

            killmail_body.get_or_create_attackers(km, killmail_body)

        return km

    def update_or_create_from_killmail(
        self, killmail: KillmailBody
    ) -> tuple[Any, bool]:
        """Update or create new EveKillmail from a Killmail object."""
        with transaction.atomic():
            try:
                self.get(killmail_id=killmail.killmail_id).delete()
                created = False
            except self.model.DoesNotExist:
                created = True
            obj = self.create_from_killmail(killmail)
        return obj, created
