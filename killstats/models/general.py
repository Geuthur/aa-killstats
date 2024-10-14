# Django
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission

# AA Killstats
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class General(models.Model):
    """A model defining commonly used properties and methods for Voices of War."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app, Killstats."),
            ("admin_access", "Has access to all killstats."),
        )

    @classmethod
    def basic_permission(cls):
        """Return basic permission needed to use this app."""
        return Permission.objects.select_related("content_type").get(
            content_type__app_label=cls._meta.app_label, codename="basic_access"
        )

    @classmethod
    def users_with_basic_access(cls) -> models.QuerySet:
        """Return users which have at least basic access to Voices of War."""
        return users_with_permission(cls.basic_permission())
