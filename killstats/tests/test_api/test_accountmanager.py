import unittest
from unittest.mock import MagicMock, patch

from django.core.exceptions import ObjectDoesNotExist

from killstats.api.account_manager import AccountManager

MODULE_PATH = "killstats.api.account_manager"


class Test_AccountManager(unittest.TestCase):
    def setUp(self):
        self.account_manager = AccountManager()
        self.account_manager.entities = {
            20000001,
            20000002,
            20000003,
            30000001,
            30000002,
            30000003,
        }

    @patch(MODULE_PATH + ".EveCharacter")
    def test_process_character_in_corporation(self, MockEveCharacter):
        char = MockEveCharacter()
        char.corporation_id = 20000001
        char.alliance_id = 1
        char.character_ownership.user.profile.main_character = char
        characters = {}
        chars_list = set()

        self.account_manager._process_character(char, characters, chars_list)

        self.assertIn(char.character_id, chars_list)
        self.assertIn(char, characters[char.character_id]["alts"])

    @patch(MODULE_PATH + ".EveCharacter")
    def test_process_character_in_alliance(self, MockEveCharacter):
        char = MockEveCharacter()
        char.corporation_id = 1
        char.alliance_id = 30000001
        char.character_ownership.user.profile.main_character = char
        characters = {}
        chars_list = set()

        self.account_manager._process_character(char, characters, chars_list)

        self.assertIn(char.character_id, chars_list)
        self.assertIn(char, characters[char.character_id]["alts"])

    @patch(MODULE_PATH + ".EveCharacter")
    def test_process_character_not_in_entities(self, MockEveCharacter):
        char = MockEveCharacter()
        char.corporation_id = 100
        char.alliance_id = 10
        char.character_ownership.user.profile.main_character = char
        characters = {}
        chars_list = set()

        self.account_manager._process_character(char, characters, chars_list)

        self.assertIn(char.character_id, characters)
        self.assertNotIn(char, characters[char.character_id]["alts"])
        self.assertNotIn(char.character_id, chars_list)
