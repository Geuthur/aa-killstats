from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist
from django.test import RequestFactory, TestCase
from django.urls import reverse

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from app_utils.testing import create_user_from_evecharacter

from killstats.api.account_manager import AccountManager
from killstats.api.killstats.api_helper import get_alliances, get_corporations
from killstats.tests.testdata.load_allianceauth import load_allianceauth

MODULE_PATH = "killstats.api.account_manager"


class TestApiHelpers(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        cls.factory = RequestFactory()

        cls.user, cls.char_owner = create_user_from_evecharacter(
            1001,
            permissions=[
                "killstats.basic_access",
            ],
        )
        cls.user2, _ = create_user_from_evecharacter(
            1002,
            permissions=[
                "killstats.basic_access",
            ],
        )
        cls.user3, _ = create_user_from_evecharacter(
            1003,
        )
        cls.user4, _ = create_user_from_evecharacter(
            1004,
        )
        cls.user5, _ = create_user_from_evecharacter(
            1005,
        )
        cls.corp = EveCorporationInfo.objects.get(corporation_id=20000001)

    def test_get_main_and_alts_all_char_in_chars(self):
        # given
        mains = {}
        request = self.factory.get("/")
        request.user = self.user
        chars = EveCharacter.objects.filter(
            corporation_id__in=[self.corp.corporation_id]
        )
        for char in chars:
            mains[char.character_id] = {"main": char, "alts": [char]}
        excepted_data = mains
        account = AccountManager(entities=[self.corp.corporation_id])
        # when
        data, _ = account.get_mains_alts()
        # then
        self.assertEqual(data, excepted_data)

    @patch(MODULE_PATH + ".EveCharacter.objects.select_related")
    def test_get_main_and_alts_all_process_object_does_not_exist(
        self, mock_select_related
    ):
        # Setup mock EveCharacter instance to simulate ObjectDoesNotExist
        mock_select_related.return_value.get.side_effect = ObjectDoesNotExist

        # Setup the rest of your test environment as before
        mains = {}
        request = self.factory.get("/")
        request.user = self.user
        chars = EveCharacter.objects.filter(
            corporation_id__in=[self.corp.corporation_id]
        )
        for char in chars:
            mains[char.character_id] = {"main": char, "alts": [char]}
        account = AccountManager(entities=[self.corp.corporation_id])
        # when
        data, _ = account.get_mains_alts()

    def test_process_character(self):
        # Create mock main character
        main_char = EveCharacter(character_id=1002, corporation_id=20000002)

        # Mock char with a main character
        char = EveCharacter(character_id=1001, corporation_id=20000001)
        char.character_ownership = self.char_owner
        char.character_ownership.user.profile.main_character = main_char

        # Test main not in characters
        characters = {}
        chars_list = set()

        account = AccountManager(entities=[20000001])

        account._process_character(char, characters, chars_list)

        # Test main in characters
        characters = {1002: {"main": main_char, "alts": []}}
        chars_list = set()

        account._process_character(char, characters, chars_list)

        # Test Corporation exist
        characters = {}
        chars_list = set()

        account._process_character(
            char,
            characters,
            chars_list,
        )

        # Test Corporation not exist
        char = EveCharacter(character_id=1001, corporation_id=20000001)
        characters = {}
        chars_list = set()

        account._process_character(char, characters, chars_list)

        # Test Attribute Error
        error = EveCorporationInfo.objects.get(corporation_id=20000001)
        characters = {}
        chars_list = set()

        account._process_character(error, characters, chars_list)

        # Test Missing character
        char = EveCharacter(character_id=9999, corporation_id=20000001)
        characters = {}
        chars_list = set()

        account._process_character(char, characters, chars_list)

        # Test Corporation & Alliance Empty
        account = AccountManager()
        char = EveCharacter(character_id=1001, corporation_id=20000001)
        characters = {}
        chars_list = set()

        account._process_character(char, characters, chars_list)

    def test_no_corp_or_ally(self):

        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user

        corp_list = get_corporations(request)

        expected_data = []

        self.assertEqual(corp_list, expected_data)

        ally_list = get_alliances(request)

        expected_data = []

        self.assertEqual(ally_list, expected_data)
