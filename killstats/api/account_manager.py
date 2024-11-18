from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from allianceauth.eveonline.models import EveCharacter

from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class AccountManager:
    def __init__(self, entities=None) -> None:
        self.entities = entities if entities is not None else []

    def _get_linked_characters(self):
        query_filter = Q(corporation_id__in=self.entities)
        query_filter |= Q(
            character_ownership__user__profile__main_character__corporation_id__in=self.entities
        )
        query_filter |= Q(alliance_id__in=self.entities)
        query_filter |= Q(
            character_ownership__user__profile__main_character__alliance_id__in=self.entities
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

    def _process_character(self, char: EveCharacter, characters: dict, chars_list: set):
        try:
            main = char.character_ownership.user.profile.main_character
            if main and main.character_id not in characters:
                characters[main.character_id] = {"main": main, "alts": []}
            if (
                char.corporation_id in self.entities
                or char.alliance_id in self.entities
            ):
                characters[main.character_id]["alts"].append(char)
                chars_list.add(char.character_id)
        except ObjectDoesNotExist:
            if EveCharacter.objects.filter(character_id=char.character_id).exists():
                char = EveCharacter.objects.get(character_id=char.character_id)
                characters[char.character_id] = {"main": char, "alts": []}
                if (
                    char.corporation_id in self.entities
                    or char.alliance_id in self.entities
                ):
                    chars_list.add(char.character_id)
                    characters[char.character_id]["alts"].append(char)
        except AttributeError:
            pass

    def get_mains_alts(self):
        """Get all members for given corporations/alliances"""
        characters = {}
        chars_list = set()

        linked_chars = self._get_linked_characters()

        for char in linked_chars:
            self._process_character(char, characters, chars_list)
        return characters, list(chars_list)
