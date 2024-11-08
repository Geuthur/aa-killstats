from django.db.models import Q, Sum

from killstats.api.account_manager import AccountManager
from killstats.api.helpers import get_alliances, get_corporations
from killstats.api.killboard_manager import (
    format_killmail,
    format_killmail_details,
    killboard_hall,
)
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Killmail

logger = get_extension_logger(__name__)

KILLMAIL_MAPPING = {
    0: "killmail_id",
    1: "victim_ship__name",
    2: "victim",
    3: "victim__name",
    4: "victim_total_value",
    5: "killmail_date",
}


# pylint: disable=too-many-locals, too-many-positional-arguments
def get_killmails_data(request, month, year, entity_id: int, mode, entity_type: str):
    if entity_id == 0:
        if entity_type == "alliance":
            entities = get_alliances(request)
        else:
            entities = get_corporations(request)
    else:
        entities = [entity_id]

    # Datatables parameters
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 25))
    limit = start + length

    search_value = request.GET.get("search[value]", "")
    order_column_index = int(request.GET.get("order[0][column]", 0))
    order_dir = request.GET.get("order[0][dir]", "desc")
    order_column = KILLMAIL_MAPPING.get(order_column_index, "killmail_date")
    order_by = f"{'-' if order_dir == 'desc' else ''}{order_column}"

    killmails = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by(order_by)
    ).filter_entities(entities)

    if mode == "losses":
        killmails = killmails.filter_entities_losses(entities)
    else:
        killmails = killmails.filter_entities_kills(entities)

    totalvalue = (
        killmails.aggregate(totalvalue=Sum("victim_total_value"))["totalvalue"],
    )

    if search_value:
        killmails = killmails.filter(
            Q(victim__name__icontains=search_value)
            | Q(victim_ship__name__icontains=search_value)
            | Q(victim_total_value__icontains=search_value)
            | Q(killmail_date__icontains=search_value)
        )

    total_count = killmails.count()
    record_count = killmails.count()
    killmails = killmails[start:limit]

    output = []
    for killmail in killmails:
        output.append(
            {
                "killmail_id": killmail.killmail_id,
                "killmail_date": killmail.killmail_date,
                "victim": {
                    "id": killmail.victim_id,
                    "name": killmail.victim.name if killmail.victim else "Unknown",
                },
                "victim_ship": {
                    "id": killmail.victim_ship_id,
                    "name": (
                        killmail.victim_ship.name if killmail.victim_ship else "Unknown"
                    ),
                },
                "victim_corporation_id": killmail.victim_corporation_id,
                "victim_alliance_id": killmail.victim_alliance_id,
                "hash": killmail.hash,
                "victim_total_value": killmail.victim_total_value,
                "victim_fitted_value": killmail.victim_fitted_value,
                "victim_destroyed_value": killmail.victim_destroyed_value,
                "victim_dropped_value": killmail.victim_dropped_value,
                "victim_region_id": killmail.victim_region_id,
                "victim_solar_system_id": killmail.victim_solar_system_id,
                "victim_position_x": killmail.victim_position_x,
                "victim_position_y": killmail.victim_position_y,
                "victim_position_z": killmail.victim_position_z,
            }
        )

    return {
        "draw": int(request.GET.get("draw", 1)),
        "recordsTotal": total_count,
        "recordsFiltered": total_count if not search_value else record_count,
        "data": output,
        "totalvalue": totalvalue,
    }


def get_killstats_halls(request, month, year, entity_id: int, entity_type: str):
    if entity_id == 0:
        if entity_type == "alliance":
            entities = get_alliances(request)
        else:
            entities = get_corporations(request)
    else:
        entities = [entity_id]

    # Ensure that only Corporation Kills are shown
    if any(entity > 10000000 for entity in entities):
        entities = [entity for entity in entities if entity >= 10000000]

    if entity_type == "alliance":
        account = AccountManager(alliances=entities)
    else:
        account = AccountManager(corporations=entities)

    killmails = (
        Killmail.objects.prefetch_related("victim", "victim_ship").filter(
            killmail_date__year=year,
            killmail_date__month=month,
        )
    ).filter_entities(entities)

    if entity_id == 0:
        mains, _ = account.get_mains_alts()
    else:
        mains = []

    shame, fame = killboard_hall(killmails, entities, mains)

    halls = []
    halls.append(
        {
            "shame": shame,
            "fame": fame,
        }
    )

    return halls


def get_entities(request, entity_id: int, entity_type: str):
    if entity_id == 0:
        if entity_type == "alliance":
            entities = get_alliances(request)
        else:
            entities = get_corporations(request)
    else:
        entities = [entity_id]

    # Ensure that only Corporation Kills are shown
    if any(entity > 10000000 for entity in entities):
        entities = [entity for entity in entities if entity >= 10000000]

    return entities


def get_top_victim(request, month, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    top_victim_querry = killmail_year.get_top_victim_stats(entities)

    if not top_victim_querry:
        return {}

    top_victim_dict = format_killmail_details(
        top_victim_querry,
        title="Top Victim:",
        count=top_victim_querry.kill_count,
        stats_type="character",
    )

    return top_victim_dict


def get_top_killer(request, month, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    top_killer_querry = killmail_year.get_top_killer_stats(entities)

    if not top_killer_querry:
        return {}

    top_killer_dict = format_killmail_details(
        top_killer_querry,
        title="Top Killer:",
        count=top_killer_querry.kill_count,
        stats_type="character",
    )

    return top_killer_dict


def get_alltime_victim(request, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    alltime_victim_querry = killmail_year.get_top_victim_stats(entities)

    if not alltime_victim_querry:
        return {}

    alltime_victim_dict = format_killmail_details(
        alltime_victim_querry,
        title="Alltime Victim:",
        count=alltime_victim_querry.kill_count,
        stats_type="character",
    )

    return alltime_victim_dict


def get_alltime_killer(request, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    alltime_killer_querry = killmail_year.get_top_killer_stats(entities)

    if not alltime_killer_querry:
        return {}

    alltime_killer_dict = format_killmail_details(
        alltime_killer_querry,
        title="Alltime Killer:",
        count=alltime_killer_querry.kill_count,
        stats_type="character",
    )

    return alltime_killer_dict


def get_worst_ship(request, month, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    worst_ship_querry = killmail_year.get_worst_ship_stats(entities)

    if not worst_ship_querry:
        return {}

    worst_ship_dict = format_killmail_details(
        worst_ship_querry,
        loss=True,
        title="Worst Ship:",
        count=worst_ship_querry.ship_count,
        stats_type="ship",
    )

    return worst_ship_dict


def get_top_ship(request, month, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    top_ship_querry = killmail_year.get_top_ship_stats(entities)

    if not top_ship_querry:
        return {}

    top_ship_dict = format_killmail_details(
        top_ship_querry,
        title="Top Ship:",
        count=top_ship_querry.ship_count,
        stats_type="ship",
    )

    return top_ship_dict


def get_top_kill(request, month, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    top_kill_querry = killmail_year.get_highest_kill_stats(entities)

    if not top_kill_querry:
        return {}

    top_kill_dict = format_killmail(
        top_kill_querry,
        title="Top Kill:",
    )

    return top_kill_dict


def get_top_loss(request, month, year, entity_id: int, entity_type: str) -> dict:
    entities = get_entities(request, entity_id, entity_type)

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    top_loss_querry = killmail_year.get_highest_loss_stats(entities)

    if not top_loss_querry:
        return {}

    top_loss_dict = format_killmail(
        top_loss_querry,
        title="Top Loss:",
    )

    return top_loss_dict
