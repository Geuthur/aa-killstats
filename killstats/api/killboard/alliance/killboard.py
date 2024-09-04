"""API"""

# Standard Library
from typing import List

from ninja import NinjaAPI

# AA Killstats
from killstats.api import schema
from killstats.api.killboard.killboard_helper import (
    get_killmails_data,
    get_killstats_halls,
    get_killstats_stats,
)
from killstats.hooks import get_extension_logger
from killstats.models.killstatsaudit import AlliancesAudit

logger = get_extension_logger(__name__)


class KillboardAllianceApiEndpoints:
    tags = ["Killboard"]

    def __init__(self, api: NinjaAPI):
        # Killmails
        @api.get(
            "killmail/month/{month}/year/{year}/alliance/{alliance_id}/{mode}/",
            response={200: dict, 403: str},
            tags=self.tags,
        )
        def get_alliance_killmails(
            request, month, year, alliance_id: int, mode, page_size: int = 100
        ):
            return get_killmails_data(
                request, month, year, alliance_id, mode, page_size, "alliance"
            )

        # Hall of Fame/Shame
        @api.get(
            "halls/month/{month}/year/{year}/alliance/{alliance_id}/",
            response={200: List[schema.KillboardHall], 403: str},
            tags=self.tags,
        )
        def get_halls(request, month, year, alliance_id: int):
            return get_killstats_halls(request, month, year, alliance_id, "alliance")

        # Stats
        @api.get(
            "stats/month/{month}/year/{year}/alliance/{alliance_id}/",
            response={200: List[schema.KillboardStats], 403: str},
            tags=self.tags,
        )
        def get_killstats(request, month, year, alliance_id: int):
            return get_killstats_stats(request, month, year, alliance_id, "alliance")

        # Admin
        @api.get(
            "killboard/alliance/admin/",
            response={200: List[schema.AllianceAdmin], 403: str},
            tags=self.tags,
        )
        def get_corporation_admin(request):
            alliances = AlliancesAudit.objects.visible_to(request.user)

            if alliances is None:
                return 403, "Permission Denied"

            alliance_dict = {}

            for alliance in alliances:
                # pylint: disable=broad-exception-caught
                try:
                    alliance_dict[alliance.alliance.alliance_id] = {
                        "alliance_id": alliance.alliance.alliance_id,
                        "alliance_name": alliance.alliance.alliance_name,
                    }
                except Exception:
                    continue

            output = []
            output.append({"alliance": alliance_dict})

            return output
