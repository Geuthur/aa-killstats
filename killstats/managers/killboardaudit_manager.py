from django.db import models

from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class KillsboardAuditQuerySet(models.QuerySet):
    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            logger.debug(
                "Returning all corps for superuser %s.",
                user,
            )
            return self

        # Admins get all visible
        if user.has_perm("killstats.admin_access"):
            logger.debug("Returning all corps for Admin %s.", user)
            return self

        return self.none()


class KillstatsAuditManager(models.Manager):
    def get_queryset(self):
        return KillsboardAuditQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)


KillstatsManager = KillstatsAuditManager.from_queryset(KillsboardAuditQuerySet)
