"""Killboard API endpoints."""

# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI
from ninja.decorators import decorate_view

# Django
from django.db.models.aggregates import Count, Sum
from django.views.decorators.cache import cache_page

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Killstats
from killstats import __title__
from killstats.api import schema
from killstats.api.helpers import (
    _build_main_name_map,
    _date_filters_attacker,
    _date_filters_killmail,
    _entity_attacker_q,
    _entity_victim_q,
)
from killstats.models.killboard import Attacker, Killmail
from killstats.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class ApiEndpoints:
    tags = ["Killboard v2"]

    def __init__(self, api: NinjaAPI):
        self.register_endpoints(api)

    def register_endpoints(self, api: NinjaAPI):
        @api.get(
            "stats/v2/summary/year/{year}/month/{month}/{entity_type}/{entity_id}/",
            response={
                HTTPStatus.OK: schema.CombatSummaryResponse,
                HTTPStatus.FORBIDDEN: dict,
            },
            tags=self.tags,
            summary="Fast summary: total kills, ISK & active PvPers",
        )
        # pylint: disable=too-many-positional-arguments
        @decorate_view(cache_page(60 * 5))  # Cache the response for 5 minutes
        def get_combat_summary_api(
            request, year: int, month: int, entity_type: str, entity_id: int
        ):
            if not request.user.has_perm("killstats.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": "Permission denied."}

            # Kills side
            attacker_q = _entity_attacker_q(entity_type, entity_id)
            kill_filters = [attacker_q, *_date_filters_attacker(year, month)]
            kill_qs = Attacker.objects.filter(*kill_filters)

            # Get distinct killmail IDs for the attacker queryset
            killmail_ids = kill_qs.values_list("killmail_id", flat=True).distinct()
            total_kills = killmail_ids.count()

            # Count active PvPers (distinct characters who participated in kills)
            active_pvpers = (
                kill_qs.exclude(character_id__isnull=True)
                .values("character_id")
                .distinct()
                .count()
            )

            # Calculate destroyed ISK for the attacker side
            destroyed_isk = (
                Killmail.objects.filter(killmail_id__in=killmail_ids).aggregate(
                    total=Sum("victim_total_value")
                )["total"]
                or 0
            )

            # Losses side
            victim_q = _entity_victim_q(entity_type, entity_id)
            loss_filters = [victim_q, *_date_filters_killmail(year, month)]
            lost_isk = (
                Killmail.objects.filter(*loss_filters).aggregate(
                    total=Sum("victim_total_value")
                )["total"]
                or 0
            )

            return schema.CombatSummaryResponse(
                total_kills=total_kills,
                active_pvpers=active_pvpers,
                destroyed_isk=destroyed_isk,
                lost_isk=lost_isk,
            )

        @api.get(
            "stats/v2/attackers/year/{year}/month/{month}/{entity_type}/{entity_id}/",
            response={
                HTTPStatus.OK: schema.TopPilotsResponse,
                HTTPStatus.FORBIDDEN: dict,
            },
            tags=self.tags,
            summary="Top-10 attackers for an entity",
        )
        @decorate_view(cache_page(60 * 5))  # Cache the response for 5 minutes
        # pylint: disable=too-many-positional-arguments
        def get_top_attackers_api(
            request,
            year: int,
            month: int,
            entity_type: str,
            entity_id: int,
            limit: int = 10,
        ):
            if not request.user.has_perm("killstats.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": "Permission denied."}

            alt_mapping = _build_main_name_map(entity_type, entity_id)

            attacker_q = _entity_attacker_q(entity_type, entity_id)
            kill_filters = [attacker_q, *_date_filters_attacker(year, month)]

            top_qs = (
                Attacker.objects.filter(*kill_filters)
                .values("character_id", "character__name")
                .annotate(
                    kills=Count("killmail_id", distinct=True),
                    total_value=Sum("killmail__victim_total_value"),
                )
                .order_by("-kills", "character__name")[:limit]
            )

            pilots = [
                schema.TopPilotSchema(
                    character_id=row["character_id"],
                    character_name=row["character__name"] or "Unknown",
                    main_name=alt_mapping.get(row["character_id"]),
                    count=row["kills"],
                    total_value=row["total_value"] or 0,
                )
                for row in top_qs
            ]

            return schema.TopPilotsResponse(pilots=pilots)

        @api.get(
            "stats/v2/victims/year/{year}/month/{month}/{entity_type}/{entity_id}/",
            response={
                HTTPStatus.OK: schema.TopPilotsResponse,
                HTTPStatus.FORBIDDEN: dict,
            },
            tags=self.tags,
            summary="Top-10 victims for an entity",
        )
        @decorate_view(cache_page(60 * 5))  # Cache the response for 5 minutes
        # pylint: disable=too-many-positional-arguments
        def get_top_victims_api(
            request,
            year: int,
            month: int,
            entity_type: str,
            entity_id: int,
            limit: int = 10,
        ):
            if not request.user.has_perm("killstats.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": "Permission denied."}

            alt_mapping = _build_main_name_map(entity_type, entity_id)

            victim_q = _entity_victim_q(entity_type, entity_id)
            loss_filters = [victim_q, *_date_filters_killmail(year, month)]

            top_qs = (
                Killmail.objects.filter(*loss_filters)
                .exclude(victim_id__isnull=True)
                .values("victim_id", "victim__name")
                .annotate(
                    deaths=Count("killmail_id", distinct=True),
                    total_value=Sum("victim_total_value"),
                )
                .order_by("-deaths", "victim__name")[:limit]
            )

            pilots = [
                schema.TopPilotSchema(
                    character_id=row["victim_id"],
                    character_name=row["victim__name"] or "Unknown",
                    main_name=alt_mapping.get(row["victim_id"]),
                    count=row["deaths"],
                    total_value=row["total_value"] or 0,
                )
                for row in top_qs
            ]

            return schema.TopPilotsResponse(pilots=pilots)
