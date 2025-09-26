"""Managers for killboard."""

# Standard Library
from typing import TYPE_CHECKING, Any

# Django
from django.db import models, transaction

if TYPE_CHECKING:
    # AA Killstats
    from killstats.helpers.killmail import KillmailBody

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Killstats
from killstats import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


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
            return self.exclude(victim_ship__eve_group__eve_category_id=65)
        return self.filter(victim_ship__eve_group__eve_category_id=65)

    def filter_threshold(self, threshold: int):
        """Filter Killmails are in Threshold."""
        return self.filter(victim_total_value__gt=threshold)


class KillmailQueryMining(KillmailQueryCore):
    def filter_barge(self):
        """Filter Mining Barge."""
        return self.filter(victim_ship__eve_group_id=463)

    def filter_exhumer(self):
        """Filter Exhumer."""
        return self.filter(victim_ship__eve_group_id=543)

    def filter_indu_command_ship(self):
        """Filter Industrial Command Ship."""
        return self.filter(victim_ship__eve_group_id=941)

    def filter_capital_indu_ship(self):
        """Filter Capital Industrial Ship."""
        return self.filter(victim_ship__eve_group_id=883)


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


class KillmailBaseManager(models.Manager):
    def get_queryset(self):
        return KillmailQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)

    def create_from_killmail(self, killmail: "KillmailBody"):
        """create a new EveKillmail from a Killmail object and returns it"""
        # AA Killstats
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Killmail

        with transaction.atomic():
            attackers_list = []

            corporation_id = killmail.victim.corporation_id
            region_id = killmail.get_or_create_region_id(killmail.solar_system_id)
            victim_ship = killmail.get_or_create_evetype(killmail.victim.ship_type_id)
            victim = None

            if killmail.victim.character_id:
                victim = killmail.get_or_create_entity(killmail.victim.character_id)
            elif killmail.victim.alliance_id:
                victim = killmail.get_or_create_entity(killmail.victim.alliance_id)
            elif killmail.victim.corporation_id:
                victim = killmail.get_or_create_entity(killmail.victim.corporation_id)

            for attacker in killmail.attackers:
                if attacker.character_id:
                    attackers_list.append(attacker.character_id)

            if attackers_list:
                try:
                    unique_attackers = list(set(attackers_list))
                    killmail.create_names_bulk(eve_ids=unique_attackers)
                # pylint: disable=broad-exception-caught
                except Exception as e:
                    logger.debug("Error on Create Names: %s", e, exc_info=True)

            km = Killmail.objects.create(
                killmail_id=killmail.id,
                killmail_date=killmail.time,
                victim=victim,
                victim_ship=victim_ship,
                victim_corporation_id=corporation_id,
                victim_alliance_id=killmail.victim.alliance_id,
                hash=killmail.zkb.hash,
                victim_total_value=killmail.zkb.total_value,
                victim_fitted_value=killmail.zkb.fitted_value,
                victim_destroyed_value=killmail.zkb.destroyed_value,
                victim_dropped_value=killmail.zkb.dropped_value,
                victim_region_id=region_id,
                victim_solar_system_id=killmail.solar_system_id,
                victim_position_x=killmail.position.x,
                victim_position_y=killmail.position.y,
                victim_position_z=killmail.position.z,
            )

            killmail.create_attackers(km, killmail)

        return km

    def update_or_create_from_killmail(
        self, killmail: "KillmailBody"
    ) -> tuple[Any, bool]:
        """Update or create new EveKillmail from a Killmail object."""
        with transaction.atomic():
            try:
                self.get(killmail_id=killmail.id).delete()
                created = False
            except self.model.DoesNotExist:
                created = True
            obj = self.create_from_killmail(killmail)
        return obj, created


EveKillmailManager = KillmailBaseManager.from_queryset(KillmailQuerySet)
