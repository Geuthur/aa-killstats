from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from allianceauth.eveonline.models import EveCharacter

from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class AccountManager:
    def __init__(self, corporations=None, alliances=None) -> None:
        self.corporations = corporations if corporations is not None else []
        self.alliances = alliances if alliances is not None else []

    def _get_linked_characters(self):
        query_filter = Q()
        if self.corporations:
            query_filter = Q(corporation_id__in=self.corporations)
            query_filter |= Q(
                character_ownership__user__profile__main_character__corporation_id__in=self.corporations
            )
        else:
            query_filter = Q(alliance_id__in=self.alliances)
            query_filter |= Q(
                character_ownership__user__profile__main_character__alliance_id__in=self.alliances
            )

        linked_chars = EveCharacter.objects.filter(query_filter)
        return (
            linked_chars.select_related(
                "character_ownership",
                "character_ownership__user__profile__main_character",
            )
            .prefetch_related("character_ownership__user__character_ownerships")
            .order_by("character_name")
        )

    def _process_character(
        self, char: EveCharacter, characters: dict, chars_list: set, missing_chars: set
    ):
        try:
            main = char.character_ownership.user.profile.main_character
            if main and main.character_id not in characters:
                characters[main.character_id] = {"main": main, "alts": []}
            if (
                char.corporation_id in self.corporations
                or char.alliance_id in self.alliances
            ):
                characters[main.character_id]["alts"].append(char)
                chars_list.add(char.character_id)
        except ObjectDoesNotExist:
            if EveCharacter.objects.filter(character_id=char.character_id).exists():
                char = EveCharacter.objects.get(character_id=char.character_id)
                characters[char.character_id] = {"main": char, "alts": []}
                if (
                    char.corporation_id in self.corporations
                    or char.alliance_id in self.alliances
                ):
                    chars_list.add(char.character_id)
                    characters[char.character_id]["alts"].append(char)
            # Not implemented yet
            missing_chars.add(char.character_id)
        except AttributeError:
            pass

    def get_mains_alts(self):
        """Get all members for given corporations/alliances"""
        characters = {}
        chars_list = set()
        missing_chars = set()

        linked_chars = self._get_linked_characters()

        for char in linked_chars:
            self._process_character(char, characters, chars_list, missing_chars)
        return characters, list(chars_list)
