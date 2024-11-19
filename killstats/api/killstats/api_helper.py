import hashlib

from django.core.cache import cache
from django.db.models import Q, Sum
from eveuniverse.models import EveEntity

from killstats.api.account_manager import AccountManager
from killstats.api.helpers import get_alliances, get_corporations
from killstats.api.killboard_manager import (
    format_killmail,
    format_killmail_details,
    killboard_hall,
)
from killstats.app_settings import KILLBOARD_API_CACHE_LIFETIME
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit

logger = get_extension_logger(__name__)

KILLMAIL_MAPPING = {
    0: "killmail_id",
    1: "victim_ship__name",
    2: "victim",
    3: "victim__name",
    4: "victim_total_value",
    5: "killmail_date",
}


def set_cache_key(cache_key, output, timeout=KILLBOARD_API_CACHE_LIFETIME):
    if not cache_key:
        return False

    logger.debug("Cache Set: %s", cache_key)
    cache.set(
        key=cache_key,
        value=output,
        timeout=timeout,
    )
    return True


def cache_sytem(request, cache_name, entity_id) -> tuple:
    cache_id = get_unique_id(request, entity_id)

    cache_key = f"{cache_name}_{cache_id}"
    output = cache.get(cache_key)

    if output is not None:
        logger.debug("Cache hit: %s", cache_key)
        return output, None
    return None, cache_key


def get_unique_id(request, entity_id) -> str:
    if entity_id != 0:
        return entity_id

    corp = get_corporations(request)
    ally = get_alliances(request)
    corp_ids = CorporationsAudit.objects.filter(
        corporation__corporation_id__in=corp
    ).values_list("corporation__corporation_id", flat=True)
    ally_ids = AlliancesAudit.objects.filter(
        alliance__alliance_id__in=ally
    ).values_list("alliance__alliance_id", flat=True)
    entities = list(corp_ids) + list(ally_ids)

    # Combine all IDs into a single string
    combined_ids = "_".join(map(str, sorted(entities)))

    # Create a unique ID from the combined IDs
    unique_id = hashlib.md5(combined_ids.encode()).hexdigest()
    return unique_id


def get_entities(request, entity_type: str, entity_id: int):
    if entity_id == 0:
        if entity_type == "alliance":
            entities = get_alliances(request)
        else:
            entities = get_corporations(request)
    else:
        entities = [entity_id]
    return entities


# pylint: disable=too-many-locals, too-many-positional-arguments
def get_killmails_data(request, month, year, entity_type: str, entity_id: int, mode):
    entities = get_entities(request, entity_type, entity_id)

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


def get_killstats_halls(request, month, year, entity_type: str, entity_id: int):
    entities = get_entities(request, entity_type, entity_id)
    account = AccountManager(entities=entities)
    mains, _ = account.get_mains_alts()

    killmails = (
        Killmail.objects.prefetch_related("victim", "victim_ship").filter(
            killmail_date__year=year,
            killmail_date__month=month,
        )
    ).filter_entities(entities)

    shame, fame = killboard_hall(killmails, entities, mains)

    halls = []
    halls.append(
        {
            "shame": shame,
            "fame": fame,
        }
    )

    return halls


def get_top_victim(request, month, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_top_killer(request, month, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_alltime_victim(request, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_alltime_killer(request, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_worst_ship(request, month, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_top_ship(request, month, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_top_kill(request, month, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_top_loss(request, month, year, entity_type: str, entity_id: int) -> dict:
    entities = get_entities(request, entity_type, entity_id)

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


def get_top_10(request, month, year, entity_type: str, entity_id: int) -> list:
    entities = get_entities(request, entity_type, entity_id)
    account = AccountManager(entities=entities)
    mains_dict, _ = account.get_mains_alts()

    killmail = (
        Killmail.objects.prefetch_related("victim", "victim_ship")
        .filter(killmail_date__year=year, killmail_date__month=month)
        .order_by("-killmail_date")
    ).filter_entities(entities)

    km_ids = killmail.values_list("killmail_id", flat=True)

    top_10_querry = killmail.get_top_10_killers(entities, km_ids)

    if not top_10_querry:
        return {}

    # Convert QuerySet to list
    top_10_list = list(top_10_querry)

    # Add character_name to each entry
    for entry in top_10_list:
        character_id = entry["character_id"]
        try:
            character = EveEntity.objects.get(id=character_id)
            entry["character_name"] = character.name

            # Check if the character is an alt and add the main character's name
            for main_id, data in mains_dict.items():
                alts = [alt.character_id for alt in data["alts"]]
                if character_id in alts and character_id != main_id:
                    main_character = data["main"]
                    entry["character_name"] += f" ({main_character.character_name})"
                    break
        except EveEntity.DoesNotExist:
            entry["character_name"] = "Unknown"
        except AttributeError:
            entry["character_name"] = "Unknown"

    return top_10_list
