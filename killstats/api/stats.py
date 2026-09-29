"""New API Endpoints for Killboard V2."""

# Standard Library
from http import HTTPStatus
from typing import Literal

# Third Party
from ninja import NinjaAPI
from ninja.decorators import decorate_view

# Django
from django.db.models import Count, Prefetch, Q, Sum
from django.views.decorators.cache import cache_page

# Alliance Auth (External Libs)
from eve_sde.models import SolarSystem

# AA Killstats
from killstats.api import schema
from killstats.api.helpers import (
    _build_main_name_map,
    _date_filters_attacker,
    _date_filters_killmail,
    _entity_attacker_q,
    _entity_victim_q,
)
from killstats.models import Attacker, Killmail


class ApiEndpoints:
    tags = ["Killboard Stats v2"]

    def __init__(self, api: NinjaAPI):
        self.register_stats(api)
        self.register_hall(api)
        self.register_killmails(api)

    def register_stats(self, api: NinjaAPI):
        @api.get(
            "stats/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/",
            response={
                HTTPStatus.OK: schema.CombatStatsResponse,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.INTERNAL_SERVER_ERROR: str,
            },
            tags=self.tags,
        )
        @decorate_view(cache_page(60 * 5))  # Cache the response for 5 minutes
        # pylint: disable=too-many-locals
        def get_stats_endpoint(
            request,
            year: int,
            month: int,
            entity_type: Literal["alliance", "corporation", "character"],
            entity_id: int,
        ):
            if not request.user.has_perm("killstats.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": "Permission denied."}

            try:
                # Build a mapping of main character names for the entity
                alt_mapping = _build_main_name_map(entity_type, entity_id)

                # Build the queryset for kills by the entity within the specified date range
                attacker_q = _entity_attacker_q(entity_type, entity_id)
                kill_filters = [attacker_q, *_date_filters_attacker(year, month)]
                kill_qs = (
                    Attacker.objects.filter(*kill_filters)
                    # Pull killmail.victim_total_value via FK in a single join
                    .select_related("character", "killmail")
                )

                # pylint: disable=duplicate-code
                # Distinct killmail IDs for the entity
                killmail_ids = kill_qs.values_list("killmail_id", flat=True).distinct()

                total_kills = killmail_ids.count()

                # Calculate the number of active PvP characters for the entity within the specified date range
                active_pvpers = (
                    kill_qs.exclude(character_id__isnull=True)
                    .values("character_id")
                    .distinct()
                    .count()
                )

                # Calculate the total ISK destroyed by the entity within the specified date range
                destroyed_isk = (
                    Killmail.objects.filter(killmail_id__in=killmail_ids).aggregate(
                        total=Sum("victim_total_value")
                    )["total"]
                    or 0
                )

                # Top-10 attackers: annotate kills and total ISK per character
                top_attackers_killmails = (
                    kill_qs.exclude(character_id__isnull=True)
                    .values("character_id", "character__name")
                    .annotate(
                        kills=Count("killmail_id", distinct=True),
                        total_value=Sum("killmail__victim_total_value"),
                    )
                    .order_by("-kills")[:10]
                )

                top_attackers = [
                    # pylint: disable=duplicate-code
                    schema.TopPilotSchema(
                        character_id=row["character_id"],
                        character_name=row["character__name"] or "Unknown",
                        main_name=alt_mapping.get(row["character_id"]),
                        count=row["kills"],
                        total_value=row["total_value"] or 0,
                    )
                    for row in top_attackers_killmails
                ]

                # Build the queryset for losses by the entity within the specified date range
                victim_q = _entity_victim_q(entity_type, entity_id)
                loss_filters = [victim_q, *_date_filters_killmail(year, month)]
                loss_qs = Killmail.objects.filter(*loss_filters).select_related(
                    "victim"
                )

                # Calculate the total ISK lost by the entity within the specified date range
                lost_isk = (
                    loss_qs.aggregate(total=Sum("victim_total_value"))["total"] or 0
                )

                # Top-10 victims
                top_victim_killmails = (
                    loss_qs.exclude(victim_id__isnull=True)
                    .values("victim_id", "victim__name")
                    .annotate(
                        deaths=Count("killmail_id", distinct=True),
                        total_value=Sum("victim_total_value"),
                    )
                    .order_by("-deaths")[:10]
                )

                top_victims = [
                    # pylint: disable=duplicate-code
                    schema.TopPilotSchema(
                        character_id=km["victim_id"],
                        character_name=km["victim__name"] or "Unknown",
                        main_name=alt_mapping.get(km["victim_id"]),
                        count=km["deaths"],
                        total_value=km["total_value"] or 0,
                    )
                    for km in top_victim_killmails
                ]

                return HTTPStatus.OK, schema.CombatStatsResponse(
                    total_kills=total_kills,
                    active_pvpers=active_pvpers,
                    destroyed_isk=destroyed_isk,
                    lost_isk=lost_isk,
                    top_attackers=top_attackers,
                    top_victims=top_victims,
                )
            except Exception as e:  # pylint: disable=broad-except
                return HTTPStatus.INTERNAL_SERVER_ERROR, str(e)

    def register_hall(self, api: NinjaAPI):
        @api.get(
            "hall/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/",
            response={
                HTTPStatus.OK: schema.HallResponseSchema,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.INTERNAL_SERVER_ERROR: str,
            },
            tags=self.tags,
        )
        @decorate_view(cache_page(60 * 5))  # Cache the response for 5 minutes
        # pylint: disable=too-many-positional-arguments, too-many-locals
        def get_hall_endpoint(
            request,
            year: int,
            month: int,
            entity_type: Literal["alliance", "corporation", "character"],
            entity_id: int,
            limit: int = 5,
        ):
            if not request.user.has_perm("killstats.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": "Permission denied."}

            try:
                # Determine the query for the attacker's killmails based on the entity type.
                if entity_type == "alliance":
                    attacker_km_q = Q(attacker_killmail__alliance_id=entity_id)
                elif entity_type == "corporation":
                    attacker_km_q = Q(attacker_killmail__corporation_id=entity_id)
                elif entity_type == "character":
                    attacker_km_q = Q(attacker_killmail__character_id=entity_id)
                else:
                    attacker_km_q = Q()

                # Fetch the top killmails for the given entity and time period.
                fame_killmails = list(
                    Killmail.objects.filter(
                        attacker_km_q, *_date_filters_killmail(year, month)
                    )
                    .distinct()
                    .select_related("victim", "victim_ship")
                    .order_by("-victim_total_value")[:limit]
                )
                top_km_ids = [km.killmail_id for km in fame_killmails]

                # For each of the top killmails, find the best attacker from the entity.
                best_attackers_by_km = {}
                if top_km_ids:
                    entity_attackers = (
                        Attacker.objects.filter(
                            _entity_attacker_q(entity_type, entity_id),
                            killmail_id__in=top_km_ids,
                        )
                        .select_related("character", "ship")
                        .order_by("-damage_done", "-final_blow")
                    )
                    for att in entity_attackers:
                        if att.killmail_id not in best_attackers_by_km:
                            best_attackers_by_km[att.killmail_id] = att

                hall_of_fame = []
                for km in fame_killmails:
                    a = best_attackers_by_km.get(km.killmail_id)
                    if not a:
                        continue
                    hall_of_fame.append(
                        schema.HallEntrySchema(
                            killmail_id=km.killmail_id,
                            char_id=a.character_id or 0,
                            char_name=a.character.name if a.character else "Unknown",
                            ship_id=a.ship_id or 0,
                            ship_name=a.ship.name if a.ship else "Unknown",
                            victim_ship_id=km.victim_ship_id or 0,
                            victim_ship_name=(
                                km.victim_ship.name if km.victim_ship else "Unknown"
                            ),
                            total_value=km.victim_total_value,
                            damage_done=a.damage_done or 0,
                            zkb_link=f"https://zkillboard.com/kill/{km.killmail_id}/",
                        )
                    )

                # --- Hall of Shame (losses) ---
                shame_filters = [
                    _entity_victim_q(entity_type, entity_id),
                    *_date_filters_killmail(year, month),
                ]

                shame_killmails = (
                    Killmail.objects.filter(*shame_filters)
                    .select_related("victim", "victim_ship")
                    .order_by("-victim_total_value")[:limit]
                )

                hall_of_shame = [
                    schema.HallEntrySchema(
                        killmail_id=km.killmail_id,
                        char_id=km.victim_id or 0,
                        char_name=km.victim.name if km.victim else "Unknown",
                        ship_id=km.victim_ship_id or 0,
                        ship_name=km.victim_ship.name if km.victim_ship else "Unknown",
                        victim_ship_id=km.victim_ship_id or 0,
                        victim_ship_name=(
                            km.victim_ship.name if km.victim_ship else "Unknown"
                        ),
                        total_value=km.victim_total_value,
                        damage_done=0,
                        zkb_link=f"https://zkillboard.com/kill/{km.killmail_id}/",
                    )
                    for km in shame_killmails
                ]

                return HTTPStatus.OK, schema.HallResponseSchema(
                    hall_of_fame=hall_of_fame, hall_of_shame=hall_of_shame
                )
            except Exception as e:  # pylint: disable=broad-except
                return HTTPStatus.INTERNAL_SERVER_ERROR, str(e)

    def register_killmails(self, api: NinjaAPI):
        @api.get(
            "killmails/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/",
            response={
                HTTPStatus.OK: schema.KillmailListResponse,
                HTTPStatus.FORBIDDEN: dict,
                HTTPStatus.INTERNAL_SERVER_ERROR: str,
            },
            tags=self.tags,
        )
        @decorate_view(cache_page(60 * 5))  # Cache the response for 5 minutes
        # pylint: disable=too-many-positional-arguments, too-many-locals, too-many-branches, too-many-arguments
        def get_killmails_endpoint(
            request,
            year: int,
            month: int,
            entity_type: Literal["alliance", "corporation", "character"],
            entity_id: int,
            mode: Literal["all", "kills", "losses"] = "all",
            page: int = 1,
            page_size: int = 50,
        ):
            if not request.user.has_perm("killstats.basic_access"):
                return HTTPStatus.FORBIDDEN, {"error": "Permission denied."}

            try:
                page_num = max(1, page)
                page_size = min(max(1, page_size), 250)
                offset = (page_num - 1) * page_size

                q = Q()
                if mode in ("kills", "all"):
                    # Filter killmails based on the attacker's entity type and ID.
                    if entity_type == "alliance":
                        q |= Q(attacker_killmail__alliance_id=entity_id)
                    elif entity_type == "corporation":
                        q |= Q(attacker_killmail__corporation_id=entity_id)
                    elif entity_type == "character":
                        q |= Q(attacker_killmail__character_id=entity_id)

                if mode in ("losses", "all"):
                    q |= _entity_victim_q(entity_type, entity_id)

                # Apply date filters to the killmail queryset.
                km_filters = [q, *_date_filters_killmail(year, month)]
                killmails = (
                    Killmail.objects.filter(*km_filters)
                    .distinct()
                    .select_related(
                        "victim",
                        "victim_ship",
                    )
                    .prefetch_related(
                        Prefetch(
                            "attacker_killmail",
                            queryset=Attacker.objects.filter(
                                final_blow=True
                            ).select_related(
                                "character"  # EveEntity FK → name for final-blow attacker
                            ),
                            to_attr="final_blow_attacker",
                        )
                    )
                )

                # Count the total number of killmails after applying filters.
                total = killmails.count()

                # Sliced killmails list with annotated pilot count
                km_slice = list(
                    killmails.annotate(
                        pilot_count=Count("attacker_killmail", distinct=True)
                    ).order_by("-killmail_date")[offset : offset + page_size]
                )

                # Bulk resolve solar systems in a single query (fixes N+1 problem)
                system_ids = {
                    km.victim_solar_system_id
                    for km in km_slice
                    if km.victim_solar_system_id
                }
                system_map = (
                    {s.id: s for s in SolarSystem.objects.filter(id__in=system_ids)}
                    if system_ids
                    else {}
                )

                # Initialize the list that will hold the serialized killmail data.
                killmails_list = []
                for km in km_slice:
                    final_blow_id = 0
                    final_blow_name = "Unknown"
                    security_status = 0.0
                    solar_system_name = "Unknown"

                    fb_list = getattr(km, "final_blow_attacker", [])
                    if fb_list:
                        fb = fb_list[0]
                        final_blow_id = fb.character_id or 0
                        final_blow_name = (
                            fb.character.name if fb.character else "Unknown"
                        )

                    solar_system = system_map.get(km.victim_solar_system_id)
                    if solar_system:
                        solar_system_name = solar_system.name
                        security_status = solar_system.security_status

                    is_loss = False
                    if entity_type == "alliance":
                        is_loss = km.victim_alliance_id == entity_id
                    elif entity_type == "corporation":
                        is_loss = km.victim_corporation_id == entity_id
                    elif entity_type == "character":
                        is_loss = km.victim_id == entity_id

                    killmails_list.append(
                        schema.KillmailItemSchema(
                            killmail_id=km.killmail_id,
                            killmail_date=km.killmail_date.isoformat(),
                            victim_id=km.victim_id or 0,
                            victim_name=km.victim.name if km.victim else "Unknown",
                            victim_ship_id=km.victim_ship_id or 0,
                            victim_ship_name=(
                                km.victim_ship.name if km.victim_ship else "Unknown"
                            ),
                            total_value=km.victim_total_value,
                            solar_system_id=km.victim_solar_system_id or 0,
                            solar_system_name=solar_system_name,
                            security_status=security_status,
                            pilot_count=km.pilot_count,
                            final_blow_id=final_blow_id,
                            final_blow_name=final_blow_name,
                            is_loss=is_loss,
                            zkb_link=f"https://zkillboard.com/kill/{km.killmail_id}/",
                        )
                    )
                return HTTPStatus.OK, schema.KillmailListResponse(
                    killmails=killmails_list,
                    total=total,
                    page=page_num,
                    page_size=page_size,
                )
            except Exception as e:  # pylint: disable=broad-except
                return HTTPStatus.INTERNAL_SERVER_ERROR, str(e)
