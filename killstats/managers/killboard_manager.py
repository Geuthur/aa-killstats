"""Managers for killboard."""

# Standard Library
from typing import Any, Tuple

# Django
from django.db import models, transaction

# AA Voices of War
from killstats.hooks import get_extension_logger
from killstats.managers.killmail_core import KillmailManager

logger = get_extension_logger(__name__)


class KillmailQueryCore(models.QuerySet):
    def filter_entities(self, entities):
        """Filter Kills and Losses from Entities List (Corporations or Alliances)."""
        kms = []
        for killmail in self:
            if any(
                attacker["corporation_id"] in entities
                for attacker in killmail.attackers
            ):
                kms.append(killmail.killmail_id)
            if killmail.victim_corporation_id in entities:
                kms.append(killmail.killmail_id)
            if any(
                attacker["alliance_id"] in entities for attacker in killmail.attackers
            ):
                kms.append(killmail.killmail_id)
            if killmail.victim_alliance_id in entities:
                kms.append(killmail.killmail_id)
        return self.filter(killmail_id__in=kms)

    def filter_entities_kills(self, entities):
        """Filter Kills from Entities List (Corporations or Alliances)."""
        kms = []
        for killmail in self:
            if any(
                attacker["corporation_id"] in entities
                for attacker in killmail.attackers
            ):
                kms.append(killmail.killmail_id)
            if any(
                attacker["alliance_id"] in entities for attacker in killmail.attackers
            ):
                kms.append(killmail.killmail_id)
        return self.filter(killmail_id__in=kms)

    def filter_entities_losses(self, entities):
        """Filter Losses from Entities List (Corporations or Alliances)."""
        kms = []
        for killmail in self:
            if killmail.victim.eve_id in entities:
                kms.append(killmail.killmail_id)
            if killmail.victim_corporation_id in entities:
                kms.append(killmail.killmail_id)
            if killmail.victim_alliance_id in entities:
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

    def filter_top_killer(self, mains):
        """Returns Topkiller from Killmail as dict."""
        topkiller = {}
        for killmail in self:
            for attacker in killmail.attackers:
                character_id, alt_char = self._find_main_or_alt(attacker, mains)
                if not character_id:
                    continue
                self._update_topkiller(topkiller, character_id, killmail, alt_char)
        return topkiller

    def _find_main_or_alt(self, attacker, mains):
        """Finds the main character or alt character based on attacker info."""
        character_id = attacker.get("character_id", 0)
        if character_id in mains:
            main_data = mains[character_id]
            return main_data["main"].character_id, None
        for main_data in mains.values():
            for alt in main_data["alts"]:
                if character_id == alt.character_id:
                    return main_data["main"].character_id, alt
        return None, None

    def _update_topkiller(self, topkiller, character_id, killmail, alt_char):
        """Updates the topkiller dictionary with the highest value killmail."""
        current_highest_value, _ = topkiller.get(character_id, (None, None))
        if (
            current_highest_value is None
            or killmail.victim_total_value > current_highest_value.victim_total_value
        ):
            topkiller[character_id] = (killmail, alt_char)


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

    def create_from_killmail(self, killmail: KillmailManager):
        """create a new EveKillmail from a Killmail object and returns it"""
        # AA Killstats
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Killmail

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

        _, new_entry = Killmail.objects.get_or_create(
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
            attackers=killmail.attackers_distinct_info(),
        )
        return new_entry

    def update_or_create_from_killmail(
        self, killmail: KillmailManager
    ) -> Tuple[Any, bool]:
        """Update or create new EveKillmail from a Killmail object."""
        with transaction.atomic():
            try:
                self.get(id=killmail.id).delete()
                created = False
            except self.model.DoesNotExist:
                created = True
            obj = self.create_from_killmail(killmail)
        return obj, created


EveKillmailManager = KillmailBaseManager.from_queryset(KillmailQuerySet)
