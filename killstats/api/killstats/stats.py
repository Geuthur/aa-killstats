"""API"""

from ninja import NinjaAPI

from django.http import JsonResponse
from django.shortcuts import render

# AA Killstats
from killstats.api.killstats import api_helper
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class KillboardStatsApiEndpoints:
    tags = ["Stats"]

    # pylint: disable=too-many-locals
    def __init__(self, api: NinjaAPI):
        self.register_endpoints(api)

    def register_endpoints(self, api: NinjaAPI):
        @api.get(
            "stats/top/victim/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_victim_api(request, month, year, entity_type: str, entity_id: int):
            top_victim = api_helper.get_top_victim(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": top_victim,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/killer/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_killer_api(request, month, year, entity_type: str, entity_id: int):
            top_killer = api_helper.get_top_killer(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": top_killer,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/alltime_victim/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        # pylint: disable=unused-argument
        def get_alltime_victim_api(
            request, month, year, entity_type: str, entity_id: int
        ):
            alltime_victim = api_helper.get_alltime_victim(
                request=request,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": alltime_victim,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/alltime_killer/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        # pylint: disable=unused-argument
        def get_alltime_killer_api(
            request, month, year, entity_type: str, entity_id: int
        ):
            alltime_killer = api_helper.get_alltime_killer(
                request=request,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": alltime_killer,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/ship/worst/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_worst_ship_api(request, month, year, entity_type: str, entity_id: int):
            worst_ship = api_helper.get_worst_ship(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": worst_ship,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/ship/top/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_ship_api(request, month, year, entity_type: str, entity_id: int):
            top_ship = api_helper.get_top_ship(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": top_ship,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/kill/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_kill_api(request, month, year, entity_type: str, entity_id: int):
            top_kill = api_helper.get_top_kill(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": top_kill,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/loss/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_loss_api(request, month, year, entity_type: str, entity_id: int):
            top_loss = api_helper.get_top_loss(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            output = []
            output.append(
                {
                    "stats": top_loss,
                }
            )
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/10/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_10_api(request, month, year, entity_type: str, entity_id: int):
            top_10 = api_helper.get_top_10(
                request=request,
                month=month,
                year=year,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            return render(
                request,
                "killstats/partials/information/view_top_10.html",
                {"top10": top_10},
            )
