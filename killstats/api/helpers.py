from allianceauth.eveonline.models import EveCharacter

from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class KillboardDate:
    def __init__(self, month, year):
        self.month = int(month)
        self.year = int(year)


def evaluate_killmail_type(killmail):
    if killmail.victim is not None:
        return killmail.victim.id
    if killmail.victim_corporation_id is not None:
        return killmail.victim_corporation_id
    if killmail.victim_alliance_id is not None:
        return killmail.victim_alliance_id
    return "Unknown", None


def get_corporations(request):
    linked_characters = request.user.profile.main_character.character_ownership.user.character_ownerships.select_related(
        "character", "user"
    ).all()

    linked_characters = linked_characters.values_list("character_id", flat=True)
    chars = EveCharacter.objects.filter(id__in=linked_characters)

    corporations = set()

    for char in chars:
        corporations.add(char.corporation_id)

    return list(corporations)


def get_alliances(request):
    linked_characters = request.user.profile.main_character.character_ownership.user.character_ownerships.select_related(
        "character", "user"
    ).all()

    linked_characters = linked_characters.values_list("character_id", flat=True)
    chars = EveCharacter.objects.filter(id__in=linked_characters)

    alliances = set()

    for char in chars:
        alliances.add(char.alliance_id)

    return list(alliances)
