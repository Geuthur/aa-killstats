"""API"""

from ninja import NinjaAPI

from django.http import JsonResponse
from django.views.decorators.cache import cache_page

# AA Killstats
from killstats.api import schema
from killstats.api.killstats.api_helper import get_killmails_data, get_killstats_halls
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class KillboardApiEndpoints:
    tags = ["Killboard"]

    def __init__(self, api: NinjaAPI):
        self.register_endpoints(api)

    def register_endpoints(self, api: NinjaAPI):
        # Killmails
        @api.get(
            "killmail/month/{month}/year/{year}/{entity_type}/{entity_id}/{mode}/",
            response={200: dict, 403: str},
            tags=self.tags,
        )
        @cache_page(60 * 10)
        # pylint: disable=too-many-positional-arguments
        def get_corporation_killmails(
            request, month, year, entity_type: str, entity_id: int, mode
        ):
            output = get_killmails_data(
                request, month, year, entity_type, entity_id, mode
            )
            return JsonResponse(output, safe=False)

        # Hall of Fame/Shame
        @api.get(
            "halls/month/{month}/year/{year}/{entity_type}/{entity_id}/",
            response={200: list[schema.KillboardHall], 403: str},
            tags=self.tags,
        )
        @cache_page(60 * 10)
        def get_corporation_halls(
            request, month, year, entity_type: str, entity_id: int
        ):
            output = get_killstats_halls(request, month, year, entity_type, entity_id)
            return JsonResponse(output, safe=False)
