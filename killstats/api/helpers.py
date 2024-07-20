from django.core.exceptions import ObjectDoesNotExist

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


def _get_linked_characters(corporations):
    linked_chars = EveCharacter.objects.filter(corporation_id__in=corporations)
    linked_chars |= EveCharacter.objects.filter(
        character_ownership__user__profile__main_character__corporation_id__in=corporations
    )
    return (
        linked_chars.select_related(
            "character_ownership", "character_ownership__user__profile__main_character"
        )
        .prefetch_related("character_ownership__user__character_ownerships")
        .order_by("character_name")
    )


def _process_character(
    char: EveCharacter, characters, chars_list, corporations, missing_chars
):
    try:
        main = char.character_ownership.user.profile.main_character
        if main and main.character_id not in characters:
            characters[main.character_id] = {"main": main, "alts": []}
        if char.corporation_id in corporations:
            characters[main.character_id]["alts"].append(char)
            chars_list.add(char.character_id)
    except ObjectDoesNotExist:
        if EveCharacter.objects.filter(character_id=char.character_id).exists():
            char = EveCharacter.objects.get(character_id=char.character_id)
            characters[char.character_id] = {"main": char, "alts": []}
            if char.corporation_id in corporations:
                chars_list.add(char.character_id)
                characters[char.character_id]["alts"].append(char)

        missing_chars.add(char.character_id)
    except AttributeError:
        pass


def get_main_and_alts_all(corporations: list):
    """Get all members for given corporations"""
    characters = {}
    chars_list = set()
    missing_chars = set()

    linked_chars = _get_linked_characters(corporations)
    corpmember = get_corp_models_and_string()

    for char in linked_chars:
        _process_character(char, characters, chars_list, corporations, missing_chars)

    for member in corpmember.objects.filter(
        corpstats__corp__corporation_id__in=corporations
    ).exclude(character_id__in=chars_list):
        char = (
            EveCharacter.objects.select_related(
                "character_ownership",
                "character_ownership__user__profile__main_character",
            )
            .prefetch_related("character_ownership__user__character_ownerships")
            .get(character_id=member.character_id)
        )
        _process_character(char, characters, chars_list, corporations, missing_chars)

    # TODO Maybe create task for missing_chars if needed

    return characters, list(chars_list)


def get_corporations(request):
    linked_characters = request.user.profile.main_character.character_ownership.user.character_ownerships.all().values_list(
        "character_id", flat=True
    )
    chars = EveCharacter.objects.filter(id__in=linked_characters)

    corporations = set()

    for char in chars:
        corporations.add(char.corporation_id)

    return corporations
