from django.db import models

# Alliance Auth (External Libs)
from allianceauth.eveonline.evelinks import eveimageserver

# AA Killstats
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Attacker, Killmail

logger = get_extension_logger(__name__)


def killboard_process_kills(killmail_data: Killmail, entities):
    killmail_data = killmail_data.prefetch_related("victim", "victim_ship")
    kills = []
    losses = []
    totalvalue = 0
    totalvalue_loss = 0

    for killmail in killmail_data.filter_entities_kills(entities):
        _stats_killmail(killmail, kills)
        totalvalue += killmail.victim_total_value

    for killmail in killmail_data.filter_entities_losses(entities):
        _stats_killmail(killmail, losses)
        totalvalue_loss += killmail.victim_total_value

    return kills, totalvalue, losses, totalvalue_loss


def _evulate_portrait(killmail, mode="killmail"):
    eve_id = killmail.victim.id
    portrait = eveimageserver.character_portrait_url(eve_id, 256)
    if killmail.victim.category == "corporation":
        portrait = eveimageserver.corporation_logo_url(eve_id, 256)
    if killmail.victim.category == "alliance":
        portrait = eveimageserver.alliance_logo_url(eve_id, 256)
    if mode == "ship":
        portrait = eveimageserver.type_render_url(eve_id, 256)
    return portrait


def _evaluate_zkb_link(killmail):
    zkb = f"https://zkillboard.com/character/{killmail.victim.id}/"
    if killmail.victim.category == "corporation":
        zkb = f"https://zkillboard.com/corporation/{killmail.victim.id}/"
    if killmail.victim.category == "alliance":
        zkb = f"https://zkillboard.com/alliance/{killmail.victim.id}/"
    return zkb


def _get_character_details(killmail, mains, entities):
    if entities is None:
        entities = []

    attackers = Attacker.objects.filter(
        models.Q(corporation_id__in=entities)
        | models.Q(alliance_id__in=entities)
        | models.Q(character_id__in=entities),
        killmail=killmail,
    )

    main = None
    alt = None

    for attacker in attackers:
        if attacker.character_id in mains:
            main = mains[attacker.character_id]["main"]
            alt = None
            break
        if mains and attacker.character_id in mains.values():
            main = mains[attacker.character_id]["main"]
            alt = attacker
            break
        alt = None
        main = attacker

    return main, alt


def _stats_killmail(
    killmail: Killmail,
    stats: list,
    mains=None,
    entities=None,
    title=None,
    count=0,
    mode="killmail",
):
    character_id = killmail.victim.id
    character_name = killmail.victim.name
    portrait = _evulate_portrait(killmail, mode)
    zkb_link = _evaluate_zkb_link(killmail)

    main, alt = _get_character_details(killmail, mains, entities)

    if main or alt:
        try:
            main_id = alt.character.id if alt is not None else 0
            main_name = "Unknown"
            if isinstance(main, Attacker):
                main_id = main.character.id
                main_name = main.character.name
            else:
                main_id = main.character_id
                main_name = main.character_name
            character_id = main_id
            character_name = (
                f"{main_name}" if alt is None else f"{alt.character.name} ({main_name})"
            )
            portrait = eveimageserver.character_portrait_url(character_id, 256)
        except AttributeError:
            logger.debug(
                "Error getting character details for %s %s",
                character_id,
                character_name,
            )

    if mode == "attacker":
        zkb_link = f"https://zkillboard.com/character/{character_id}/"

    stats.append(
        {
            # zKB Data
            "killmail_id": killmail.killmail_id,
            "character_id": character_id,
            "character_name": character_name,
            "corporation_id": killmail.victim_corporation_id,
            "alliance_id": killmail.victim_alliance_id,
            "ship": killmail.victim_ship_id,
            "ship_name": (
                killmail.victim_ship.name
                if killmail.victim_ship is not None
                else "Unknown"
            ),
            "hash": killmail.hash,
            "totalValue": killmail.victim_total_value,
            "date": killmail.killmail_date,
            # Additional Data
            "title": f"{killmail.victim.name}" if title is None else title,
            "portrait": portrait,
            "zkb_link": zkb_link,
            "count": count,
        }
    )
    return stats


def killboard_dashboard(
    killmail_year: Killmail,
    date,
    entities,
):
    stats = []

    test = killmail_year.get_killboard_stats(entities, date)

    if test["highest_loss"]:
        stats.append(format_killmail(test["highest_loss"], title="Top Loss:"))
    if test["worst_ship"]:
        stats.append(
            format_killmail_details(
                test["worst_ship"],
                loss=True,
                title="Worst Ship:",
                count=test["worst_ship"].ship_count,
                stats_type="ship",
            )
        )
    if test["top_loss"]:
        stats.append(
            format_killmail_details(
                test["top_loss"],
                loss=True,
                title="Top Victim:",
                count=test["top_loss"].kill_count,
                stats_type="character",
            )
        )
    if test["alltime_loss"]:
        stats.append(
            format_killmail_details(
                test["alltime_loss"],
                loss=True,
                title="Alltime Victim:",
                count=test["alltime_loss"].kill_count,
                stats_type="character",
            )
        )
    if test["highest_kill"]:
        stats.append(format_killmail(test["highest_kill"], title="Top Kill:"))
    if test["top_ship"]:
        stats.append(
            format_killmail_details(
                test["top_ship"],
                title="Top Ship:",
                count=test["top_ship"].ship_count,
                stats_type="ship",
            )
        )
    if test["top_killer"]:
        stats.append(
            format_killmail_details(
                test["top_killer"],
                title="Top Killer:",
                count=test["top_killer"].kill_count,
                stats_type="character",
            )
        )
    if test["alltime_killer"]:
        stats.append(
            format_killmail_details(
                test["alltime_killer"],
                title="Alltime Killer:",
                count=test["alltime_killer"].kill_count,
                stats_type="character",
            )
        )

    return stats


# pylint: disable=too-many-locals
def killboard_hall(killmail_month: Killmail, entities, mains):
    # Ensure that the killmails are sorted by total value
    killmail_month = killmail_month.order_by("-victim_total_value").prefetch_related(
        "victim", "victim_ship"
    )

    shame = []
    fame = []

    topkiller = killmail_month.filter_entities_kills(entities)
    toplosses = killmail_month.filter_entities_losses(entities)

    for killmail in topkiller[:5]:
        _stats_killmail(
            killmail, stats=fame, mains=mains, mode="attacker", entities=entities
        )

    for killmail in toplosses[:5]:
        _stats_killmail(killmail, stats=shame, mains=mains)

    return shame, fame


def format_killmail(killmail: Killmail, title):
    return {
        "killmail_id": killmail.killmail_id,
        "character_id": killmail.victim.id,
        "character_name": killmail.victim.name,
        "corporation_id": killmail.victim_corporation_id,
        "alliance_id": killmail.victim_alliance_id,
        "ship": killmail.victim_ship.id,
        "ship_name": killmail.victim_ship.name,
        "hash": killmail.hash,
        "totalValue": killmail.victim_total_value,
        "date": killmail.killmail_date.isoformat(),
        "title": title,
        "portrait": f"https://images.evetech.net/types/{killmail.victim_ship.id}/icon?size=256",
        "zkb_link": f"https://zkillboard.com/character/{killmail.victim.id}/",
    }


def format_killmail_details(
    entity, loss=False, title=None, count=0, stats_type="character"
):
    if stats_type == "ship":
        return {
            "title": title,
            "type": "count",
            "ship_id": entity.id,
            "ship_name": entity.name,
            "portrait": f"https://images.evetech.net/types/{entity.id}/icon?size=256",
            "count": count,
            "loss": loss,
            "zkb_link": f"https://zkillboard.com/ship/{entity.id}/",
        }

    return {
        "title": f"{title} {entity.name}",
        "type": "count",
        "character_id": entity.id,
        "character_name": entity.name if entity.name is not None else "Unknown",
        "portrait": f"https://images.evetech.net/characters/{entity.id}/portrait?size=256",
        "count": count,
        "loss": loss,
        "zkb_link": f"https://zkillboard.com/character/{entity.id}/",
    }
