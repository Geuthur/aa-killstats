# Django
from django.contrib.auth.models import User

# Alliance Auth
from allianceauth.authentication.backends import StateBackend
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils

# Alliance Auth (External Libs)
from app_utils.testing import add_character_to_user
from eveuniverse.models import EveType

# AA Killstats
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit


def create_corporation(eve_character: EveCharacter, **kwargs) -> CorporationsAudit:
    """Create a CorporationAudit from EveCharacter"""
    params = {
        "corporation": eve_character.corporation,
        "owner": eve_character,
    }
    params.update(kwargs)
    corporation = CorporationsAudit(**params)
    corporation.save()
    return corporation


def create_user_from_evecharacter_with_access(
    character_id: int, disconnect_signals: bool = True
) -> tuple[User, CharacterOwnership]:
    """Create user with access from an existing eve character and use it as main."""
    auth_character = EveCharacter.objects.get(character_id=character_id)
    username = StateBackend.iterate_username(auth_character.character_name)
    user = AuthUtils.create_user(username, disconnect_signals=disconnect_signals)
    user = AuthUtils.add_permission_to_user_by_name(
        "killstats.basic_access", user, disconnect_signals=disconnect_signals
    )
    character_ownership = add_character_to_user(
        user,
        auth_character,
        is_main=True,
        scopes=["publicData"],
        disconnect_signals=disconnect_signals,
    )
    return user, character_ownership


def create_corporationaudit_from_character_id(
    character_id: int, **kwargs
) -> CorporationsAudit:
    """Create a Corporation Audit from a existing EveCharacter"""

    _, character_ownership = create_user_from_evecharacter_with_access(
        character_id, disconnect_signals=True
    )
    return create_corporation(character_ownership.character, **kwargs)


def create_allianceaudit_from_character_id(
    character_id: int, **kwargs
) -> AlliancesAudit:
    """Create a Alliance Audit from a existing EveCharacter"""

    _, character_ownership = create_user_from_evecharacter_with_access(
        character_id, disconnect_signals=True
    )
    return create_alliance(character_ownership.character, **kwargs)


def add_auth_character_to_user(
    user: User, character_id: int, disconnect_signals: bool = True
) -> CharacterOwnership:
    auth_character = EveCharacter.objects.get(character_id=character_id)
    return add_character_to_user(
        user,
        auth_character,
        is_main=False,
        scopes=["publicData"],
        disconnect_signals=disconnect_signals,
    )


def add_corporationaudit_character_to_user(
    user: User, character_id: int, disconnect_signals: bool = True, **kwargs
) -> CorporationsAudit:
    """Add a Character Audit Character to a user"""
    character_ownership = add_auth_character_to_user(
        user,
        character_id,
        disconnect_signals=disconnect_signals,
    )
    return create_corporation(character_ownership.character, **kwargs)


def create_alliance(eve_character: EveCharacter, **kwargs) -> AlliancesAudit:
    """Create a AllianceAudit from EveCharacter"""
    params = {
        "alliance": eve_character.alliance,
        "owner": eve_character,
    }
    params.update(kwargs)
    alliance = AlliancesAudit(**params)
    alliance.save()
    return alliance
