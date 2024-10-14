"""Managers for killboard."""

# Standard Library
from typing import Any

# Django
from django.db import models, transaction
from eveuniverse.models import EveEntity, EveType

from killstats.decorators import log_timing

# AA Voices of War
from killstats.hooks import get_extension_logger
from killstats.managers.killmail_core import KillmailManager

logger = get_extension_logger(__name__)


class KillmailQueryCore(models.QuerySet):
    def filter_entities(self, entities):
        """Filter Kills and Losses from Entities List (Corporations or Alliances)."""
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Attacker

        kms = []

        # Get all Killmail IDs
        km_ids = self.values_list("killmail_id", flat=True)

        # Get all Attackers from Entities
        kms_data = Attacker.objects.filter(
            models.Q(corporation_id__in=entities)
            | models.Q(alliance_id__in=entities)
            | models.Q(character_id__in=entities),
            killmail_id__in=km_ids,
        ).values_list("killmail_id", "corporation_id", "alliance_id")

        for killmail_id, corporation_id, alliance_id in kms_data:
            if corporation_id in entities or alliance_id in entities:
                kms.append(killmail_id)

        # Include Victim Kills
        victim_kms_ids = self.filter(
            models.Q(victim_id__in=entities)
            | models.Q(victim_corporation_id__in=entities)
            | models.Q(victim_alliance_id__in=entities)
        ).values_list("killmail_id", flat=True)

        for killmail_id in victim_kms_ids:
            kms.append(killmail_id)

        return self.filter(killmail_id__in=kms)

    def filter_entities_kills(self, entities):
        """Filter Kills from Entities List (Corporations or Alliances)."""
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Attacker

        kms = []

        # Sammle alle Angreifer-Daten
        km_ids = self.values_list("killmail_id", flat=True)

        kms_data = Attacker.objects.filter(
            models.Q(corporation_id__in=entities)
            | models.Q(alliance_id__in=entities)
            | models.Q(character_id__in=entities),
            killmail_id__in=km_ids,
        ).values_list("killmail_id", "corporation_id", "alliance_id")

        for killmail_id, corporation_id, alliance_id in kms_data:
            if corporation_id in entities or alliance_id in entities:
                kms.append(killmail_id)

        return self.filter(killmail_id__in=kms)

    def filter_entities_losses(self, entities):
        """Filter Losses from Entities List (Corporations or Alliances)."""
        kms = []

        victim_kms = self.filter(
            models.Q(victim_id__in=entities)
            | models.Q(victim_corporation_id__in=entities)
            | models.Q(victim_alliance_id__in=entities)
        )

        for killmail in victim_kms:
            kms.append(killmail.killmail_id)

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


class KillmailQueryStats(KillmailQueryMining):
    @log_timing(logger)
    def _get_top_ship(self, entities, km_ids):
        """Get the top ship for the given entities."""
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Attacker

        topship = (
            Attacker.objects.filter(
                models.Q(corporation_id__in=entities)
                | models.Q(alliance_id__in=entities)
                | models.Q(character_id__in=entities),
                killmail_id__in=km_ids,
            )
            .values("ship__id")
            .annotate(count=models.Count("ship__id"))
            .order_by("-count")
        ).first()

        if topship:
            top_ship = EveType.objects.get(id=topship["ship__id"])
            top_ship.ship_count = topship["count"]
            return top_ship
        return None

    @log_timing(logger)
    def _get_worst_ship(self, entities, km_ids):
        """Get the worst ship for the given entities."""
        losses = self.filter(
            models.Q(victim_id__in=entities)
            | models.Q(victim_corporation_id__in=entities)
            | models.Q(victim_alliance_id__in=entities),
            killmail_id__in=km_ids,
        ).exclude(victim_ship__eve_group_id=29)

        worst_ship = (
            losses.values("victim_ship_id")
            .annotate(kill_count=models.Count("victim_ship_id"))
            .order_by("-kill_count", "victim_ship__name")
        ).first()

        if worst_ship:
            ship_id = worst_ship["victim_ship_id"]
            kill_count = worst_ship["kill_count"]

            # Get the worst ship and add the kill count
            worst_ship = EveType.objects.get(id=ship_id)
            worst_ship.ship_count = kill_count
            return worst_ship

        return None

    @log_timing(logger)
    def _get_top_victim(self, entities, km_ids):
        """Get the top victim for the given entities."""
        victim = (
            self.filter(
                models.Q(victim_id__in=entities)
                | models.Q(victim_corporation_id__in=entities)
                | models.Q(victim_alliance_id__in=entities),
                killmail_id__in=km_ids,
            )
            .values("victim_id")
            .annotate(kill_count=models.Count("victim_id"))
            .order_by("-kill_count", "victim__name")
        ).first()

        if victim:
            top_victim = EveEntity.objects.get(id=victim["victim_id"])
            top_victim.kill_count = victim["kill_count"]
            return top_victim
        return None

    @log_timing(logger)
    def _get_top_killer(self, entities, km_ids):
        """Get the top killer for the given entities."""
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Attacker

        attacker = (
            Attacker.objects.filter(
                models.Q(corporation_id__in=entities)
                | models.Q(alliance_id__in=entities)
                | models.Q(character_id__in=entities),
                killmail_id__in=km_ids,
            )
            .values("character_id")
            .annotate(kill_count=models.Count("killmail_id"))
            .order_by("-kill_count", "character__name")
        ).first()

        if attacker:
            top_attacker = EveEntity.objects.get(id=attacker["character_id"])
            top_attacker.kill_count = attacker["kill_count"]
            return top_attacker
        return None

    @log_timing(logger)
    def get_killboard_stats(self, entities, date):
        """Get all killboard stats for the given entities."""
        stats = {}

        month, year = date.month, date.year

        # Common queries
        losses = self.filter_entities_losses(entities)
        kills = self.filter_entities_kills(entities)

        # Get the highest loss
        highest_loss = (
            losses.filter(killmail_date__year=year, killmail_date__month=month)
            .annotate(total_value=models.F("victim_total_value"))
            .order_by("-total_value", "-victim_fitted_value")
            .first()
        )
        stats["highest_loss"] = highest_loss

        # Get the highest kill
        highest_kill = (
            kills.filter(killmail_date__year=year, killmail_date__month=month)
            .annotate(total_value=models.F("victim_total_value"))
            .order_by("-total_value", "-victim_fitted_value")
            .first()
        )
        stats["highest_kill"] = highest_kill

        # Get Killmail IDs for the given year
        km_ids_year = kills.filter(killmail_date__year=year).values_list(
            "killmail_id", flat=True
        )
        # Get Killmail IDs for the given month
        km_ids = km_ids_year.filter(
            killmail_date__year=year,
            killmail_date__month=month,
        ).values_list("killmail_id", flat=True)
        # Get Loss Killmail IDs for the given year
        km_ids_loss_year = losses.filter(killmail_date__year=year).values_list(
            "killmail_id", flat=True
        )
        # Get Loss Killmail IDs for the given month
        km_ids_loss = km_ids_loss_year.filter(
            killmail_date__year=year,
            killmail_date__month=month,
        ).values_list("killmail_id", flat=True)

        # Get the worst ship
        stats["worst_ship"] = self._get_worst_ship(entities, km_ids_loss)

        stats["top_ship"] = self._get_top_ship(entities, km_ids)

        # Get the top killer Month
        stats["top_killer"] = self._get_top_killer(entities, km_ids)

        # Get the top killer Year
        stats["alltime_killer"] = self._get_top_killer(entities, km_ids_year)

        # Get the top victim Month
        stats["top_loss"] = self._get_top_victim(entities, km_ids_loss)

        # Get the top victim Year
        stats["alltime_loss"] = self._get_top_victim(entities, km_ids_loss_year)

        return stats


class KillmailQuerySet(KillmailQueryStats):
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

    def create_from_killmail(self, killmail: KillmailManager):
        """create a new EveKillmail from a Killmail object and returns it"""
        # AA Killstats
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Killmail

        with transaction.atomic():
            attackers_list = []

            corporation_id = killmail.victim.corporation_id
            region_id = killmail.get_region_id(killmail.solar_system_id)
            victim_ship = killmail.get_ship_name(killmail.victim.ship_type_id)
            victim = None

            if killmail.victim.character_id:
                victim = killmail.get_entity_name(killmail.victim.character_id)
            elif killmail.victim.alliance_id:
                victim = killmail.get_entity_name(killmail.victim.alliance_id)
            elif killmail.victim.corporation_id:
                victim = killmail.get_entity_name(killmail.victim.corporation_id)

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
        self, killmail: KillmailManager
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
