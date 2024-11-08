"""API"""

from ninja import NinjaAPI

# AA Killstats
from killstats.api.killboard.killboard_helper import (
    get_alltime_killer,
    get_alltime_victim,
    get_top_kill,
    get_top_killer,
    get_top_loss,
    get_top_ship,
    get_top_victim,
    get_worst_ship,
)
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class KillboardCorporationStatsApiEndpoints:
    tags = ["Stats"]

    # pylint: disable=too-many-locals
    def __init__(self, api: NinjaAPI):
        # Stats
        @api.get(
            "stats/top/victim/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_victim_api(request, month, year, corporation_id: int):
            top_victim = get_top_victim(
                request=request,
                month=month,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": top_victim,
                }
            )
            return output

        @api.get(
            "stats/top/killer/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_killer_api(request, month, year, corporation_id: int):
            top_killer = get_top_killer(
                request=request,
                month=month,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": top_killer,
                }
            )
            return output

        @api.get(
            "stats/top/alltime_victim/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        # pylint: disable=unused-argument
        def get_alltime_victim_api(request, month, year, corporation_id: int):
            alltime_victim = get_alltime_victim(
                request=request,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": alltime_victim,
                }
            )
            return output

        @api.get(
            "stats/top/alltime_killer/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        # pylint: disable=unused-argument
        def get_alltime_killer_api(request, month, year, corporation_id: int):
            alltime_killer = get_alltime_killer(
                request=request,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": alltime_killer,
                }
            )
            return output

        @api.get(
            "stats/ship/worst/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_worst_ship_api(request, month, year, corporation_id: int):
            worst_ship = get_worst_ship(
                request=request,
                month=month,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": worst_ship,
                }
            )
            return output

        @api.get(
            "stats/ship/top/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_ship_api(request, month, year, corporation_id: int):
            top_ship = get_top_ship(
                request=request,
                month=month,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": top_ship,
                }
            )
            return output

        @api.get(
            "stats/top/kill/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_kill_api(request, month, year, corporation_id: int):
            top_kill = get_top_kill(
                request=request,
                month=month,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": top_kill,
                }
            )
            return output

        @api.get(
            "stats/top/loss/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_loss_api(request, month, year, corporation_id: int):
            top_loss = get_top_loss(
                request=request,
                month=month,
                year=year,
                entity_id=corporation_id,
                entity_type="corporation",
            )

            output = []
            output.append(
                {
                    "stats": top_loss,
                }
            )
            return output
