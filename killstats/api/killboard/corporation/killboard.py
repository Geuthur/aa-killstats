"""API"""

from ninja import NinjaAPI

# AA Killstats
from killstats.api import schema
from killstats.api.killboard.killboard_helper import (
    get_killmails_data,
    get_killstats_halls,
    get_killstats_stats,
)
from killstats.hooks import get_extension_logger
from killstats.models.killstatsaudit import CorporationsAudit

logger = get_extension_logger(__name__)


class KillboardCorporationApiEndpoints:
    tags = ["Killboard"]

    # pylint: disable=too-many-locals
    def __init__(self, api: NinjaAPI):

        # Killmails
        @api.get(
            "killmail/month/{month}/year/{year}/corporation/{corporation_id}/{mode}/",
            response={200: dict, 403: str},
            tags=self.tags,
        )
        # pylint: disable=too-many-positional-arguments
        def get_corporation_killmails(request, month, year, corporation_id: int, mode):
            return get_killmails_data(
                request, month, year, corporation_id, mode, "corporation"
            )

        # Hall of Fame/Shame
        @api.get(
            "halls/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[schema.KillboardHall], 403: str},
            tags=self.tags,
        )
        def get_corporation_halls(request, month, year, corporation_id: int):
            return get_killstats_halls(
                request, month, year, corporation_id, "corporation"
            )

        # Stats
        @api.get(
            "stats/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[schema.KillboardStats], 403: str},
            tags=self.tags,
        )
        def get_corporation_killstats(request, month, year, corporation_id: int):
            return get_killstats_stats(
                request, month, year, corporation_id, "corporation"
            )

        @api.get(
            "killboard/corporation/admin/",
            response={200: list[schema.CorporationAdmin], 403: str},
            tags=self.tags,
        )
        def get_corporation_admin(request):
            corporations = CorporationsAudit.objects.visible_to(request.user)

            if corporations is None:
                return 403, "Permission Denied"

            corporation_dict = {}

            for corporation in corporations:
                # pylint: disable=broad-exception-caught
                try:
                    corporation_dict[corporation.corporation.corporation_id] = {
                        "corporation_id": corporation.corporation.corporation_id,
                        "corporation_name": corporation.corporation.corporation_name,
                    }
                except Exception:
                    continue

            output = []
            output.append({"corporation": corporation_dict})

            return output
