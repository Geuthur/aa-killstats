# Standard Library
from collections import Counter
from heapq import nlargest

from eveuniverse.models import EveType

# Alliance Auth (External Libs)
from allianceauth.eveonline.evelinks import eveimageserver

# AA Killstats
from killstats.hooks import get_extension_logger
from killstats.models.general import EveEntity
from killstats.models.killboard import Killmail

logger = get_extension_logger(__name__)


# TODO Refactor this code and make it easier...


class KillboardStatsCount:
    def __init__(self):
        self.worst_ship = 0
        self.top_victim = 0
        self.top_ship = 0
        self.top_killer = 0
        self.alltime_killer = 0
        self.alltime_loss = 0


class KillboardStatsManager:
    def __init__(self, date, stats, entities):
        self.worst_ship = Counter()
        self.top_victim = Counter()
        self.top_ship = Counter()
        self.top_killer = Counter()
        self.alltime_killer = Counter()
        self.alltime_loss = Counter()
        self.count = KillboardStatsCount()
        self.entities = entities
        self.date = date
        self.stats = stats

    def update_for_killmail(self, killmail: Killmail):
        self._update_kill_stats(killmail)

    def _update_kill_stats(self, killmail: Killmail):
        counted_ships = set()
        for attacker in killmail.attackers:
            if (
                attacker["corporation_id"] in self.entities
                or attacker["alliance_id"] in self.entities
            ):
                ship_id = attacker["ship_type_id"]
                attacker_id = attacker["character_id"]
                if ship_id not in counted_ships and killmail.get_month(self.date.month):
                    self.top_ship[ship_id] += 1
                    counted_ships.add(ship_id)
                if killmail.get_month(self.date.month):
                    self.top_killer[attacker_id] += 1
                self.alltime_killer[attacker_id] += 1
        victim_id = killmail.victim.eve_id
        if (
            killmail.victim_corporation_id in self.entities
            or killmail.victim_alliance_id in self.entities
        ):
            if killmail.get_month(self.date.month):
                if not killmail.is_capsule() and not killmail.is_mobile():
                    self.worst_ship[killmail.victim_ship.id] += 1
                self.top_victim[victim_id] += 1
            self.alltime_loss[victim_id] += 1

    def _stats_count(self, title, model, count, char=False, loss=False):
        if model:
            eve_id = model.eve_id if char else model.id

            if char:
                portrait = eveimageserver.character_portrait_url(eve_id, 256)
            else:
                portrait = eveimageserver.type_icon_url(eve_id, 256)

            key_id = "character_id" if char else "ship"
            key_name = "character_name" if char else "ship_name"
            self.stats.append(
                {
                    "title": title,
                    "type": "count",
                    key_id: eve_id,
                    key_name: model.name,
                    "portrait": f"{portrait}",
                    "count": count,
                    "loss": loss,
                    "zkb_link": f"https://zkillboard.com/character/{eve_id}/",
                }
            )

    def get_top_entity(self, counter, model):
        try:
            top_entity_id, top_entity_count = counter.most_common(1)[0]
            if model == EveType:
                top_entity = model.objects.get(id=top_entity_id)
            else:
                top_entity = model.objects.get(eve_id=top_entity_id)
            return top_entity, top_entity_count
        except IndexError:
            return None, 0

    # Losses
    def update_worst_ship(self):
        self.worst_ship, self.count.worst_ship = self.get_top_entity(
            self.worst_ship, EveType
        )
        self._stats_count(
            "Worst Ship:",
            self.worst_ship,
            self.count.worst_ship,
            loss=True,
        )

    def update_top_victim(self):
        self.top_victim, self.count.top_victim = self.get_top_entity(
            self.top_victim, EveEntity
        )
        self._stats_count(
            f"Top Victim: {self.top_victim}",
            self.top_victim,
            self.count.top_victim,
            char=True,
            loss=True,
        )

    def update_alltime_loss(self):
        self.alltime_loss, self.count.alltime_loss = self.get_top_entity(
            self.alltime_loss, EveEntity
        )
        self._stats_count(
            f"Alltime Victim: {self.alltime_loss}",
            self.alltime_loss,
            self.count.alltime_loss,
            char=True,
            loss=True,
        )

    # Kills
    def update_top_ship(self):
        self.top_ship, self.count.top_ship = self.get_top_entity(self.top_ship, EveType)
        self._stats_count("Top Ship:", self.top_ship, self.count.top_ship)

    def update_top_killer(self):
        self.top_killer, self.count.top_killer = self.get_top_entity(
            self.top_killer, EveEntity
        )
        self._stats_count(
            f"Top Killer: {self.top_killer}",
            self.top_killer,
            self.count.top_killer,
            char=True,
        )

    def update_alltime_killer(self):
        self.alltime_killer, self.count.alltime_killer = self.get_top_entity(
            self.alltime_killer, EveEntity
        )
        self._stats_count(
            f"Alltime Killer: {self.alltime_killer}",
            self.alltime_killer,
            self.count.alltime_killer,
            char=True,
        )


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
    eve_id = killmail.victim.eve_id
    portrait = eveimageserver.character_portrait_url(eve_id, 256)
    if killmail.victim.category == "corporation":
        portrait = eveimageserver.corporation_logo_url(eve_id, 256)
    if killmail.victim.category == "alliance":
        portrait = eveimageserver.alliance_logo_url(eve_id, 256)
    if mode == "ship":
        portrait = (
            f"https://images.evetech.net/types/{killmail.victim_ship.id}/icon?size=256"
        )
    return portrait


def _evaluate_zkb_link(killmail):
    zkb = f"https://zkillboard.com/character/{killmail.victim.eve_id}/"
    if killmail.victim.category == "corporation":
        zkb = f"https://zkillboard.com/corporation/{killmail.victim.eve_id}/"
    if killmail.victim.category == "alliance":
        zkb = f"https://zkillboard.com/alliance/{killmail.victim.eve_id}/"
    return zkb


def _get_character_details(killmail, mains, mode):
    main = None
    main_id = None
    alt = None

    # Check if Victim is Main or Alt and set main and alt accordingly
    if killmail.victim.eve_id in mains:
        main_data = mains[killmail.victim.eve_id]
        main = main_data["main"]
        main_id = killmail.victim.eve_id
    else:
        for main_data in mains.values():
            alts = main_data.get("alts", [])
            for alt_candidate in alts:
                if killmail.victim.eve_id == alt_candidate.character_id:
                    main = main_data["main"]
                    alt = alt_candidate
                    break
            if alt:  # Break outer loop if alt is found
                break

    if mode == "attacker":
        main, main_id, alt = killmail.attacker_main(mains)

    return main, main_id, alt


def _stats_killmail(
    killmail: Killmail,
    stats: list,
    mains=None,
    main_list=None,
    title=None,
    count=0,
    mode="killmail",
):
    character_id = killmail.victim.eve_id
    character_name = killmail.victim.name
    portrait = _evulate_portrait(killmail, mode)
    zkb_link = _evaluate_zkb_link(killmail)

    if mains:
        main, _, alt = (
            _get_character_details(killmail, mains, mode)
            if main_list is None
            else main_list
        )

        character_id = main.character_id if alt is None else alt.character_id
        character_name = (
            f"{main.character_name}"
            if alt is None
            else f"{alt.character_name} ({main.character_name})"
        )
        portrait = eveimageserver.character_portrait_url(character_id, 256)

    stats.append(
        {
            # zKB Data
            "killmail_id": killmail.killmail_id,
            "character_id": character_id,
            "character_name": character_name,
            "corporation_id": killmail.victim_corporation_id,
            "alliance_id": killmail.victim_alliance_id,
            "ship": killmail.victim_ship.id,
            "ship_name": killmail.victim_ship.name,
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
    killmail_year = killmail_year.prefetch_related("victim", "victim_ship")

    stats = []
    stats_manager = KillboardStatsManager(date, stats, entities=entities)
    filtered_killmails_loss = [
        km for km in killmail_year if km.get_month(date.month) and km.is_loss(entities)
    ]
    filtered_killmails_kill = [
        km for km in killmail_year if km.get_month(date.month) and km.is_kill(entities)
    ]

    highest_loss = nlargest(
        1, filtered_killmails_loss, key=lambda km: km.victim_total_value
    )
    highest_kill = nlargest(
        1, filtered_killmails_kill, key=lambda km: km.victim_total_value
    )
    for killmail in killmail_year:
        stats_manager.update_for_killmail(killmail)

    # Update All Stats
    if highest_loss:
        _stats_killmail(highest_loss[0], stats, title="Top Loss:", mode="ship")
    stats_manager.update_worst_ship()
    stats_manager.update_top_victim()
    stats_manager.update_alltime_loss()

    if highest_kill:
        _stats_killmail(highest_kill[0], stats, title="Top Kill:", mode="ship")
    stats_manager.update_top_ship()
    stats_manager.update_top_killer()
    stats_manager.update_alltime_killer()

    return stats


# pylint: disable=too-many-locals
def killboard_hall(killmail_month: Killmail, entities, mains):
    # Ensure that the killmails are sorted by total value
    killmail_month = killmail_month.order_by("-victim_total_value").prefetch_related(
        "victim", "victim_ship"
    )

    shame = []
    fame = []

    topkiller = killmail_month.filter_entities_kills(entities).filter_top_killer(mains)
    toplosses = killmail_month.filter_entities_losses(entities)

    for char in topkiller:
        killmail_fame, alt_char = topkiller.get(char, (None, None))
        if alt_char:
            # Check if the attacker is an alt and get the associated main character
            for main_data in mains.values():
                for alt in main_data["alts"]:
                    if alt_char.character_id == alt.character_id:
                        main = main_data["main"]
                        main_id = char
                        alt_data = alt_char
                        break
        else:
            if char in mains:
                main_data = mains[char]
                main = main_data["main"]
                main_id = char
                alt_data = None

        main_list = [main, main_id, alt_data]

        _stats_killmail(
            killmail_fame, stats=fame, mains=mains, mode="attacker", main_list=main_list
        )

    for killmail in toplosses[:5]:
        _stats_killmail(killmail, stats=shame, mains=mains)

    return shame, fame[:5]
