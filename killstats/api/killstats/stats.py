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

    # pylint: disable=too-many-statements
    def register_endpoints(self, api: NinjaAPI):
        @api.get(
            "stats/top/victim/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_victim_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"top_victim_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/killer/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_killer_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"top_killer_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
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
            cache_name = f"alltime_victim_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
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
            cache_name = f"alltime_killer_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/ship/worst/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_worst_ship_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"worst_ship_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/ship/top/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_ship_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"top_ship_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/kill/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_kill_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"top_kill_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/loss/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_loss_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"top_loss_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
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
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return JsonResponse(output, safe=False)

        @api.get(
            "stats/top/10/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[dict], 403: str},
            tags=self.tags,
        )
        def get_top_10_api(request, month, year, entity_type: str, entity_id: int):
            cache_name = f"top_10_{month}_{year}_{entity_type}_{entity_id}"
            output, cache_key = api_helper.cache_sytem(request, cache_name, entity_id)

            if cache_key:
                top_10 = api_helper.get_top_10(
                    request=request,
                    month=month,
                    year=year,
                    entity_type=entity_type,
                    entity_id=entity_id,
                )

                output = {"top10": top_10}
                # Cache the output
                api_helper.set_cache_key(cache_key, output)
            return render(
                request,
                "killstats/partials/information/view_top_10.html",
                output,
            )
