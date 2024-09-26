from django.db.models import Q, Sum

from killstats.api.account_manager import AccountManager
from killstats.api.helpers import KillboardDate, get_alliances, get_corporations
from killstats.api.killboard_manager import killboard_dashboard, killboard_hall
from killstats.models.killboard import Killmail


# pylint: disable=too-many-locals, too-many-positional-arguments
def get_killmails_data(
    request, month, year, entity_id: int, mode, page_size: int, entity_type: str
):
    if entity_id == 0:
        if entity_type == "alliance":
            entities = get_alliances(request)
        else:
            entities = get_corporations(request)
    else:
        entities = [entity_id]

    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", page_size))
    search_value = request.GET.get("search[value]", "")
    order_column_index = int(request.GET.get("order[0][column]", 0))
    order_dir = request.GET.get("order[0][dir]", "desc")

    column_mapping = {
        0: "killmail_id",
        1: "victim_ship__name",
        2: "victim",
        3: "victim__name",
        4: "victim_total_value",
        5: "killmail_date",
    }

    order_column = column_mapping.get(order_column_index, "killmail_date")
    order_by = f"{'-' if order_dir == 'desc' else ''}{order_column}"

    offset = start
    limit = length

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
        )

    total_count = killmails.count()
    record_count = killmails.count()
    killmails = killmails[offset : offset + limit]

    output = []
    for killmail in killmails:
        output.append(
            {
                "killmail_id": killmail.killmail_id,
                "killmail_date": killmail.killmail_date,
                "victim": {
                    "id": killmail.victim.id,
                    "name": killmail.victim.name,
                },
                "victim_ship": {
                    "id": killmail.victim_ship.id,
                    "name": killmail.victim_ship.name,
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


def get_killstats_stats(request, month, year, entity_id: int, entity_type: str):
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

    killmail_year = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    date = KillboardDate(month, year)

    stats = killboard_dashboard(killmail_year, date, entities)

    output = []
    output.append(
        {
            "stats": stats,
        }
    )

    return output
