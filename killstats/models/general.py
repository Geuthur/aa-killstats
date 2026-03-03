# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Killstats
from killstats import __title__
from killstats.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class General(models.Model):
    """A model defining commonly used properties and methods for Voices of War."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app, Killstats."),
            ("admin_access", "Has access to all killstats."),
        )
