"""Admin models"""

from django_redis import get_redis_connection

from django.contrib import admin
from django.utils.html import format_html

from allianceauth.eveonline.evelinks import eveimageserver

from killstats.hooks import get_extension_logger
from killstats.models.killstatsaudit import KillstatsAudit

logger = get_extension_logger(__name__)


@admin.register(KillstatsAudit)
class KillstatsAuditAdmin(admin.ModelAdmin):
    list_display = (
        "_entity_pic",
        "_corporation__corporation_id",
        "_last_update",
    )

    list_display_links = (
        "_entity_pic",
        "_corporation__corporation_id",
    )

    list_select_related = ("corporation",)

    ordering = ["corporation__corporation_name"]

    search_fields = ["corporation__corporation_name", "corporation__corporation_id"]

    actions = ["delete_objects", "clear_cache_for_selected"]

    @admin.display(description="")
    def _entity_pic(self, obj: KillstatsAudit):
        eve_id = obj.corporation.corporation_id
        return format_html(
            '<img src="{}" class="img-circle">',
            eveimageserver._eve_entity_image_url("corporation", eve_id, 32),
        )

    @admin.display(description="Corporation ID", ordering="corporation__corporation_id")
    def _corporation__corporation_id(self, obj: KillstatsAudit):
        return obj.corporation.corporation_id

    @admin.display(description="Last Update", ordering="last_update")
    def _last_update(self, obj: KillstatsAudit):
        return obj.last_update

    # pylint: disable=unused-argument
    def has_add_permission(self, request):
        return False

    # pylint: disable=unused-argument
    def has_change_permission(self, request, obj=None):
        return False

    @admin.action(description="Clear cache for selected Corporations")
    def clear_cache_for_selected(self, request, queryset: KillstatsAudit):
        for obj in queryset:
            clear_cache_zkb(obj.corporation.corporation_id)
            logger.debug("Clearing cache for selected Corporations %s", obj.corporation)
        self.message_user(
            request, "Cache successfully cleared for selected Corporations."
        )


def clear_cache_zkb(corporation_id: int):
    conn = get_redis_connection("default")
    for key in conn.scan_iter(
        f"*:zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/{corporation_id}*"
    ):
        conn.delete(key)
        logger.debug("Deleting key %s", key)
    return True
