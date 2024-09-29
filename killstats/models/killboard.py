# Django
from django.db import models
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveEntity, EveType

# Alliance Auth
from allianceauth.eveonline.evelinks import eveimageserver

# AA Killstats
from killstats.hooks import get_extension_logger
from killstats.managers.killboard_manager import EveKillmailManager

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

    objects = EveKillmailManager()

    def __str__(self):
        return f"Killmail {self.killmail_id}"

    def get_or_unknown_victim_name(self):
        """Return the victim name or Unknown."""
        return self.victim.name if self.victim else _("Unknown")

    def get_or_unknown_victim_ship_name(self):
        """Return the victim ship name or Unknown."""
        return self.victim_ship.name if self.victim_ship else _("Unknown")

    def evaluate_victim_id(self):
        """Return the victim ID."""
        if self.victim is not None:
            return self.victim.id
        if self.victim_corporation_id is not None:
            return self.victim_corporation_id
        if self.victim_alliance_id is not None:
            return self.victim_alliance_id
        return 0

    def get_image_url(self):
        return eveimageserver._eve_entity_image_url(
            self.victim.category, self.victim.id, 32
        )

    def is_corp(self, corps: list):
        """Return True if the victim corporation is in the list of corporations."""
        attackers = Attacker.objects.filter(killmail=self).values_list(
            "corporation_id", flat=True
        )
        return self.victim_corporation_id in corps or any(
            attacker in corps for attacker in attackers
        )

    def is_alliance(self, alliances: list):
        """Return True if the victim alliance is in the list of alliances."""
        attackers = Attacker.objects.filter(killmail=self).values_list(
            "alliance_id", flat=True
        )
        return self.victim_alliance_id in alliances or any(
            attacker in alliances for attacker in attackers
        )

    def is_structure(self):
        """Return True if the victim is a structure."""
        return self.victim_ship.eve_group.eve_category_id == 65

    def is_mobile(self):
        """Return True if the victim is a mobile structure."""
        return self.victim_ship.eve_group.eve_category_id == 22

    def is_capsule(self):
        """Return True if the victim is a capsule."""
        return self.victim_ship.eve_group.id == 29

    def get_month(self, month):
        """Get all killmails of a specific month."""
        return self.killmail_date.month == month

    def threshold(self, threshold: int) -> bool:
        """Return True if the total value of the killmail is above the threshold."""
        return self.victim_total_value > threshold

    class Meta:
        default_permissions = ()


class Attacker(models.Model):
    killmail = models.ForeignKey(
        Killmail, on_delete=models.CASCADE, related_name="attacker_killmail"
    )
    character = models.ForeignKey(
        EveEntity,
        on_delete=models.CASCADE,
        related_name="attacker_character",
        null=True,
        blank=True,
    )
    corporation = models.ForeignKey(
        EveEntity,
        on_delete=models.CASCADE,
        related_name="attacker_corp",
        null=True,
        blank=True,
    )
    alliance = models.ForeignKey(
        EveEntity,
        on_delete=models.CASCADE,
        related_name="attacker_alliance",
        null=True,
        blank=True,
    )
    ship = models.ForeignKey(
        EveType,
        on_delete=models.CASCADE,
        related_name="attacker_ship",
        null=True,
        blank=True,
    )
    damage_done = models.IntegerField(null=True, blank=True)
    final_blow = models.BooleanField(null=True, blank=True)
    weapon_type_id = models.PositiveBigIntegerField(null=True, blank=True)
    security_status = models.FloatField(null=True, blank=True)

    def get_or_unknown_character_name(self):
        """Return the character name or Unknown."""
        return self.character.name if self.character else _("Unknown")

    def get_or_unknown_corporation_name(self):
        """Return the corporation name or Unknown."""
        return self.corporation.name if self.corporation else _("Unknown")

    def get_or_unknown_alliance_name(self):
        """Return the alliance name or Unknown."""
        return self.alliance.name if self.alliance else _("Unknown")

    def get_or_unknown_ship_name(self):
        """Return the ship name or Unknown."""
        return self.ship.name if self.ship else _("Unknown")

    def evaluate_attacker(self) -> tuple:
        """Return the attacker ID and Name."""
        if self.character is not None:
            return self.character.id, self.character.name
        if self.corporation is not None:
            return self.corporation.id, self.corporation.name
        if self.alliance is not None:
            return self.alliance.id, self.alliance.name
        return 0, _("Unknown")

    class Meta:
        default_permissions = ()
