import unittest
from unittest.mock import patch

from killstats.api.account_manager import AccountManager

MODULE_PATH = "killstats.api.account_manager"


class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.account_manager = AccountManager()
        self.account_manager.corporations = {1, 2, 3}
        self.account_manager.alliances = {10, 20, 30}

    @patch(MODULE_PATH + ".EveCharacter")
    def test_process_character_in_corporation(self, MockEveCharacter):
        char = MockEveCharacter()
        char.corporation_id = 1
        char.alliance_id = 100
        char.character_ownership.user.profile.main_character = char
        characters = {}
        chars_list = set()
        missing_chars = set()

        self.account_manager._process_character(
            char, characters, chars_list, missing_chars
        )

        self.assertIn(char.character_id, chars_list)
        self.assertIn(char, characters[char.character_id]["alts"])

    @patch(MODULE_PATH + ".EveCharacter")
    def test_process_character_in_alliance(self, MockEveCharacter):
        char = MockEveCharacter()
        char.corporation_id = 100
        char.alliance_id = 10
        char.character_ownership.user.profile.main_character = char
        characters = {}
        chars_list = set()
        missing_chars = set()

        self.account_manager._process_character(
            char, characters, chars_list, missing_chars
        )

        self.assertIn(char.character_id, chars_list)
        self.assertIn(char, characters[char.character_id]["alts"])

    @patch(MODULE_PATH + ".EveCharacter")
    def test_process_character_not_in_corporation_or_alliance(self, MockEveCharacter):
        char = MockEveCharacter()
        char.corporation_id = 100
        char.alliance_id = 100
        char.character_ownership.user.profile.main_character = char
        characters = {}
        chars_list = set()
        missing_chars = set()

        self.account_manager._process_character(
            char, characters, chars_list, missing_chars
        )

        self.assertNotIn(char.character_id, chars_list)
        self.assertNotIn(char, characters.get(char.character_id, {}).get("alts", []))
