"""Unit tests for AccountManager in killstats.api.account_manager."""

# EVE SDE & Alliance Auth Factories
# Third Party
from evesde_factory.allianceauth import EveCharacterFactory, UserFactory
from evesde_factory.utils import add_character_to_user

# AA Killstats
from killstats.api.account_manager import AccountManager
from killstats.tests import AuthTestCase
from killstats.tests.testdata.killstats import UserMainFactory

MODULE_PATH = "killstats.api.account_manager"


class TestAccountManager(AuthTestCase):
    def test_get_mains_alts_should_return_characters_and_id_list(self):
        # Test Data
        main_char = EveCharacterFactory()
        alt_char = EveCharacterFactory()
        user = UserMainFactory(main_character__character=main_char)
        add_character_to_user(user=user, character=alt_char)

        account_manager = AccountManager()

        # Test Action
        characters, char_id_list = account_manager.get_mains_alts()

        # Expected Result
        self.assertIn(main_char.character_id, characters)
        self.assertEqual(characters[main_char.character_id]["main"], main_char)
        self.assertIn(alt_char, characters[main_char.character_id]["alts"])
        self.assertIn(main_char.character_id, char_id_list)
        self.assertIn(alt_char.character_id, char_id_list)

    def test_get_mains_alts_should_ignore_users_without_main_character(self):
        # Test Data
        user_without_main = UserFactory()
        user_without_main.profile.main_character = None
        user_without_main.profile.save()

        account_manager = AccountManager()

        # Test Action
        characters, char_id_list = account_manager.get_mains_alts()

        # Expected Result
        all_main_ids = [data["main"].character_id for data in characters.values()]
        self.assertNotIn(None, all_main_ids)

    def test_get_mains_alts_should_return_empty_when_no_accounts_with_main_exist(
        self,
    ):
        # Test Data
        account_manager = AccountManager()
        account_manager.accounts = account_manager.accounts.none()

        # Test Action
        characters, char_id_list = account_manager.get_mains_alts()

        # Expected Result
        self.assertEqual(characters, {})
        self.assertEqual(char_id_list, [])

    def test_get_mains_alts_should_handle_multiple_accounts(self):
        # Test Data
        main1 = EveCharacterFactory()
        main2 = EveCharacterFactory()
        UserMainFactory(main_character__character=main1)
        UserMainFactory(main_character__character=main2)

        account_manager = AccountManager()

        # Test Action
        characters, char_id_list = account_manager.get_mains_alts()

        # Expected Result
        self.assertIn(main1.character_id, characters)
        self.assertIn(main2.character_id, characters)
        self.assertIn(main1.character_id, char_id_list)
        self.assertIn(main2.character_id, char_id_list)
