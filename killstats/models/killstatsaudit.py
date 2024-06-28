"""
Killstats Audit Model
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

from killstats.hooks import get_extension_logger
from killstats.managers.killboardaudit_manager import KillstatsManager

logger = get_extension_logger(__name__)


class KillstatsAudit(models.Model):

    corporation = models.OneToOneField(
        EveCorporationInfo,
        on_delete=models.CASCADE,
    )

    last_update = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(EveCharacter, on_delete=models.CASCADE)

    objects = KillstatsManager()

    def __str__(self):
        return f"{self.corporation.corporation_name}'s Killstats Data"

    class Meta:
        default_permissions = ()
