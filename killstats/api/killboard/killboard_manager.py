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
    def __init__(self, date, stats):
        self.worst_ship = Counter()
        self.top_victim = Counter()
        self.top_ship = Counter()
        self.top_killer = Counter()
        self.alltime_killer = Counter()
        self.alltime_loss = Counter()
        self.count = KillboardStatsCount()
        self.date = date
        self.stats = stats

    def update_for_killmail(self, killmail: Killmail, all_chars):
        if killmail.is_kill(all_chars):
            self._update_kill_stats(killmail, all_chars)
        if killmail.is_loss(all_chars):
            self._update_loss_stats(killmail)

    def _update_kill_stats(self, killmail: Killmail, all_chars):
        counted_ships = set()
        for attacker in killmail.attackers:
            if attacker["character_id"] in all_chars:
                ship_id = attacker["ship_type_id"]
                attacker_id = attacker["character_id"]
                if ship_id not in counted_ships and killmail.get_month(self.date.month):
                    self.top_ship[ship_id] += 1
                    counted_ships.add(ship_id)
                if killmail.get_month(self.date.month):
                    self.top_killer[attacker_id] += 1
                self.alltime_killer[attacker_id] += 1

    def _update_loss_stats(self, killmail: Killmail):
        victim_id = killmail.victim.eve_id
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


def killboard_process_kills(killmail_data: Killmail, mains, all_chars):
    kills = []
    losses = []
    totalvalue = 0
    totalvalue_loss = 0

    for killmail in killmail_data:
        if killmail.is_kill(all_chars) and not killmail.is_loss(all_chars):
            _stats_killmail(killmail, mains, kills)
            totalvalue += killmail.victim_total_value
        if killmail.is_loss(all_chars):
            _stats_killmail(killmail, mains, losses)
            totalvalue_loss += killmail.victim_total_value

    return kills, totalvalue, losses, totalvalue_loss


def _get_character_details(killmail, mains, stats_type, main_list):
    if main_list:
        return main_list

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

    if stats_type == "attacker" and not main_list:
        main, main_id, alt = killmail.attacker_main(mains, killmail.attackers)

    return main, main_id, alt


def _calculate_character_info(alt, main, main_id, stats_type, killmail, char_name):
    if stats_type == "attacker":
        if alt is None:
            character_id = main_id
            character_name = f"{main}"
        else:
            character_id = alt.character_id
            character_name = f"{alt.character_name} ({main})" if alt else char_name
    else:
        character_id = (
            killmail.victim.eve_id if killmail.victim.category == "character" else None
        )
        if main and str(char_name) != str(main):
            character_name = f"{char_name} ({main})"
        else:
            character_name = char_name

    return character_id, character_name


def _stats_killmail(
    killmail: Killmail,
    mains: dict,
    stats: list,
    title=None,
    stats_type="killmail",
    count=0,
    main_list=None,
):
    main, main_id, alt = _get_character_details(killmail, mains, stats_type, main_list)
    char_name = killmail.victim.name
    portrait = eveimageserver.type_icon_url(killmail.victim_ship.id, 64)
    character_id, character_name = _calculate_character_info(
        alt, main, main_id, stats_type, killmail, char_name
    )

    stats.append(
        {
            "title": f"{title}" if main is not None else title,
            "killmail_id": killmail.killmail_id,
            "name": char_name,
            "character_id": character_id,
            "character_name": character_name,
            "portrait": portrait,
            "corporation_id": killmail.victim_corporation_id,
            "alliance_id": killmail.victim_alliance_id,
            "ship": killmail.victim_ship.id,
            "ship_name": killmail.victim_ship.name,
            "hash": killmail.hash,
            "totalValue": killmail.victim_total_value,
            "date": killmail.killmail_date,
            "count": count,
        }
    )
    return stats


def killboard_dashboard(
    killmail_year: Killmail,
    date,
    sorted_mains,
    all_chars,
):
    stats = []
    stats_manager = KillboardStatsManager(date, stats)

    filtered_killmails = [
        km for km in killmail_year if km.is_loss(all_chars) and km.get_month(date.month)
    ]
    filtered_killmails_kill = [
        km
        for km in killmail_year
        if not km.is_capsule()
        and km.is_kill(all_chars)
        and not km.is_loss(all_chars)
        and km.get_month(date.month)
    ]

    highest_loss = nlargest(1, filtered_killmails, key=lambda km: km.victim_total_value)
    highest_kill = nlargest(
        1, filtered_killmails_kill, key=lambda km: km.victim_total_value
    )

    for killmail in killmail_year:
        stats_manager.update_for_killmail(killmail, all_chars)

    # Update All Stats
    if highest_loss:
        _stats_killmail(highest_loss[0], sorted_mains, stats, "Top Loss:", "ship")
    stats_manager.update_worst_ship()
    stats_manager.update_top_victim()
    stats_manager.update_alltime_loss()

    if highest_kill:
        _stats_killmail(highest_kill[0], sorted_mains, stats, "Top Kill:")
    stats_manager.update_top_ship()
    stats_manager.update_top_killer()
    stats_manager.update_alltime_killer()

    return stats


# pylint: disable=too-many-locals
def killboard_hall(killmail_month: Killmail, mains):
    all_chars = list(
        set(
            [main["main"].character_id for _, main in mains.items()]
            + [alt.character_id for _, main in mains.items() for alt in main["alts"]]
        )
    )

    killmail_month = killmail_month.order_by("-victim_total_value")

    shame = []
    fame = []

    topkiller = (
        killmail_month.filter_threshold(1_000_000)
        .filter_kills(all_chars)
        .filter_loss(all_chars, exclude=True)
        .filter_top_killer(mains)
    )
    toplosses = killmail_month.filter_loss(all_chars, exclude=False)

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
            killmail_fame, mains, fame, stats_type="attacker", main_list=main_list
        )

    for killmail in toplosses:
        _stats_killmail(killmail, mains, shame)

    return shame[:5], fame[:5]
