from django.db import models

# Alliance Auth (External Libs)
from allianceauth.eveonline.evelinks import eveimageserver

# AA Killstats
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Attacker, Killmail

logger = get_extension_logger(__name__)


def _get_character_details_attacker(killmail: Killmail, mains, entities, unique_killer):
    def process_attacker(attacker, mains, unique_killer):
        for mains_entry in mains.values():
            main_character = mains_entry["main"]
            alts = mains_entry["alts"]
            for alt_character in alts:
                if attacker.character_id == alt_character.character_id:
                    if attacker.character_id not in unique_killer:
                        main = main_character
                        alt = (
                            alt_character
                            if main_character.character_id != attacker.character_id
                            else None
                        )
                        character_id = (
                            main.character_id if alt is None else alt.character_id
                        )
                        character_name = (
                            f"{main.character_name}"
                            if alt is None
                            else f"{alt.character_name} ({main.character_name})"
                        )
                        unique_killer.add(attacker.character_id)
                        return character_id, character_name
        return None, None

    attackers = Attacker.objects.filter(
        models.Q(corporation_id__in=entities)
        | models.Q(alliance_id__in=entities)
        | models.Q(character_id__in=entities),
        killmail=killmail,
    )

    for attacker in attackers:
        if mains:
            character_id, character_name = process_attacker(
                attacker, mains, unique_killer
            )
            if character_id is not None:
                return character_id, character_name

    return None, None


def _get_character_details_victim(killmail: Killmail, mains):
    def process_victim(killmail, mains_entry):
        main_character = mains_entry["main"]
        alts = mains_entry["alts"]
        for alt_character in alts:
            if killmail.victim.id == alt_character.character_id:
                main = main_character
                alt = (
                    alt_character
                    if main_character.character_id != killmail.victim.id
                    else None
                )
                character_id = main.character_id if alt is None else alt.character_id
                character_name = (
                    f"{main.character_name}"
                    if alt is None
                    else f"{alt.character_name} ({main.character_name})"
                )
                return character_id, character_name
        return None, None

    try:
        for mains_entry in mains.values():
            character_id, character_name = process_victim(killmail, mains_entry)
            if character_id is not None:
                return character_id, character_name
    except AttributeError:
        pass

    return killmail.victim.id, killmail.victim.name


# pylint: disable=too-many-positional-arguments
def _hall_killmail(
    kms,
    stats: list,
    mains,
    entities=None,
    title=None,
    mode="killmail",
):
    unique_killer = set()
    for killmail in kms:
        if len(stats) >= 5:
            break

        zkb_link = killmail.evaluate_zkb_link()
        title_html = (
            f"{killmail.get_or_unknown_victim_name()}" if title is None else title
        )

        character_id, character_name = (
            _get_character_details_attacker(killmail, mains, entities, unique_killer)
            if mode == "attacker"
            else _get_character_details_victim(killmail, mains)
        )

        if character_id is None:
            continue

        portrait = eveimageserver.character_portrait_url(character_id, 256)

        if mode == "attacker":
            zkb_link = f"https://zkillboard.com/character/{character_id}/"

        stats.append(
            {
                # zKB Data
                "killmail_id": killmail.killmail_id,
                "character_id": character_id,
                "character_name": character_name,
                "ship": killmail.victim_ship_id,
                "ship_name": killmail.get_or_unknown_victim_ship_name(),
                "totalValue": killmail.victim_total_value,
                # Additional Data
                "title": title_html,
                "portrait": portrait,
                "zkb_link": zkb_link,
            }
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

    _hall_killmail(
        topkiller, stats=fame, mains=mains, mode="attacker", entities=entities
    )

    _hall_killmail(toplosses, stats=shame, mains=mains)

    return shame, fame


def format_killmail(killmail: Killmail, title):
    return {
        "killmail_id": killmail.killmail_id,
        "character_id": killmail.victim_id,
        "character_name": killmail.get_or_unknown_victim_name(),
        "corporation_id": killmail.victim_corporation_id,
        "alliance_id": killmail.victim_alliance_id,
        "ship": killmail.victim_ship_id,
        "ship_name": killmail.get_or_unknown_victim_ship_name(),
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
