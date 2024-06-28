from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.models import EveCharacter

from killstats import app_settings
from killstats.errors import KillstatsImportError
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


# pylint: disable=import-outside-toplevel
def get_corp_models_and_string():
    if app_settings.KILLSTATS_CORPSTATS_TWO:
        try:
            from corpstats.models import CorpMember

            return CorpMember
        except ImportError as exc:
            logger.error("Corpstats is enabled but not installed")
            raise KillstatsImportError(
                "Corpstats is enabled but not installed"
            ) from exc

    from allianceauth.corputils.models import CorpMember

    return CorpMember


def get_main_and_alts_all(corporations: list, char_ids=False, corp_members=True):
    """
    Get all mains and their alts from Alliance Auth if they are in Corp

    Args:
    - corporations: corp `list`
    - char_ids: include list
    - corp_members: add Corp Members

    Returns - Dict (Queryset)
    - `Dict`: Mains and Alts QuerySet (EvECharacter or CorpMember)

    Returns - Dict(Queryset) & List
    - `Dict`: Mains and Alts Queryset
    - `List`: Character IDS
    """
    mains = {}
    corpmember = get_corp_models_and_string()

    users = (
        UserProfile.objects.select_related("main_character")
        .all()
        .order_by("main_character_id")
    )

    for char in users:
        if char.main_character:
            main = char.main_character.character_ownership.user.profile.main_character
            linked_characters = (
                main.character_ownership.user.character_ownerships.all().exclude(
                    character__character_id=main.character_id
                )
            )
            if main.corporation_id in corporations:
                mains[main.character_id] = {
                    "main": main,
                    "alts": [char.character for char in linked_characters],
                }
        else:
            continue

    if corp_members:
        corp = corpmember.objects.select_related("corpstats", "corpstats__corp").filter(
            corpstats__corp__corporation_id__in=corporations
        )

        # Add Chars from Corp Stats to the Ledger
        chars = list(
            set(
                [main["main"].character_id for _, main in mains.items()]
                + [
                    alt.character_id
                    for _, main in mains.items()
                    for alt in main["alts"]
                ]
            )
        )
        for char in corp:
            try:
                char = EveCharacter.objects.get(character_id=char.character_id)
            except EveCharacter.DoesNotExist:
                pass
            if char.character_id not in chars:
                mains[char.character_id] = {"main": char, "alts": []}

    # Sort Names Alphabetic
    mains = sorted(mains.items(), key=lambda item: item[1]["main"].character_name)
    mains = dict(mains)
    if char_ids:
        chars = list(
            set(
                [main["main"].character_id for _, main in mains.items()]
                + [
                    alt.character_id
                    for _, main in mains.items()
                    for alt in main["alts"]
                ]
            )
        )
        return mains, chars
    return mains


def get_corporations(request):
    linked_characters = request.user.profile.main_character.character_ownership.user.character_ownerships.all().values_list(
        "character_id", flat=True
    )
    chars = EveCharacter.objects.filter(id__in=linked_characters)

    corporations = set()

    for char in chars:
        corporations.add(char.corporation_id)

    return corporations
