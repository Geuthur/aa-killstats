# Standard Library
from typing import Set

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from eveuniverse.models import EveType

# Alliance Auth
from allianceauth.eveonline.evelinks import eveimageserver

# AA Killstats
from killstats.hooks import get_extension_logger
from killstats.managers.killboard_manager import EveKillmailManager
from killstats.models.general import EveEntity

logger = get_extension_logger(__name__)


class Killmail(models.Model):
    killmail_id = models.PositiveBigIntegerField(primary_key=True)
    killmail_date = models.DateTimeField(null=True, blank=True)
    victim = models.ForeignKey(EveEntity, on_delete=models.CASCADE, null=True)
    victim_ship = models.ForeignKey(EveType, on_delete=models.CASCADE, null=True)
    victim_corporation_id = models.PositiveBigIntegerField()
    victim_alliance_id = models.PositiveBigIntegerField(null=True, blank=True)
    hash = models.CharField(max_length=255, unique=True)
    # Value Infos
    victim_total_value = models.PositiveBigIntegerField(null=True, blank=True)
    victim_fitted_value = models.PositiveBigIntegerField(null=True, blank=True)
    victim_destroyed_value = models.PositiveBigIntegerField(null=True, blank=True)
    victim_dropped_value = models.PositiveBigIntegerField(null=True, blank=True)
    # Location Infos
    victim_region_id = models.PositiveBigIntegerField(null=True, blank=True)
    victim_solar_system_id = models.PositiveBigIntegerField(null=True, blank=True)
    victim_position_x = models.FloatField(null=True, blank=True)
    victim_position_y = models.FloatField(null=True, blank=True)
    victim_position_z = models.FloatField(null=True, blank=True)
    # Attackers as JSON
    attackers = models.JSONField(null=True, blank=True)

    objects = EveKillmailManager()

    def __str__(self):
        return f"Killmail {self.killmail_id}"

    def get_image_url(self):
        return eveimageserver._eve_entity_image_url(
            self.victim.category, self.victim.eve_id, 32
        )

    def is_kill(self, chars: list):
        """Return True if any attacker is in the list of characters."""
        return any(attacker["character_id"] in chars for attacker in self.attackers)

    def is_loss(self, chars: list):
        """Return True if the victim is in the list of characters."""
        return self.victim.eve_id in chars if self.victim else False

    def is_corp(self, corps: list):
        """Return True if the victim corporation is in the list of corporations."""
        return self.victim_corporation_id in corps or any(
            attacker["corporation_id"] in corps for attacker in self.attackers
        )

    def is_structure(self):
        """Return True if the victim is a structure."""
        return self.victim_ship.eve_group.eve_category_id == 65

    def is_mobile(self):
        """Return True if the victim is a mobile structure."""
        return self.victim_ship.eve_group.eve_category_id == 22

    def is_capsule(self):
        """Return True if the victim is a capsule."""
        return self.victim_ship.id in (670, 33328)

    def get_month(self, month):
        """Get all killmails of a specific month."""
        return self.killmail_date.month == month

    def attackers_distinct_alliance_ids(self) -> Set[int]:
        """Return distinct alliance IDs of all attackers."""
        return [
            attacker["alliance_id"]
            for attacker in self.attackers
            if "alliance_id" in attacker
        ]

    def attackers_distinct_corporation_ids(self) -> Set[int]:
        """Return distinct corporation IDs of all attackers."""
        return [
            attacker["corporation_id"]
            for attacker in self.attackers
            if "corporation_id" in attacker
        ]

    def attackers_distinct_character_ids(self) -> Set[int]:
        """Return distinct character IDs of all attackers."""
        return [
            attacker["character_id"]
            for attacker in self.attackers
            if "character_id" in attacker
        ]

    @classmethod
    def threshold(cls, threshold: int):
        """Return True if the total value of the killmail is above the threshold."""
        return cls.objects.filter(victim_total_value__gt=threshold)

    @classmethod
    def attacker_main(cls, mains, attackers):
        """
        Get Attacker Main Data from Mains Dict

        Returns
        ----------
        - Main Name:  `str`
        - CharacterID: `int`
        - Alt Object: `object`
        """
        for attacker in attackers:
            attacker_id = attacker["character_id"]

            if attacker_id in mains:
                main_data = mains[attacker_id]
                main = main_data["main"]
                main_id = attacker_id
                return main, main_id, None

            # Check if the attacker is an alt and get the associated main character
            for main_data in mains.values():
                for alt in main_data["alts"]:
                    if attacker_id == alt.character_id:
                        main = main_data["main"]
                        main_id = attacker_id
                        attacker = alt
                        return main, main_id, attacker
        return None, None, None

    class Meta:
        default_permissions = ()
