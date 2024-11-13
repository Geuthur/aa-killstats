from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase
from django.urls import reverse
from eveuniverse.models import EveEntity

from allianceauth.eveonline.models import EveCharacter
from app_utils.testing import add_character_to_user, create_user_from_evecharacter

from killstats.api.killstats.api_helper import get_top_10
from killstats.tests.test_api import _api_helper
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.api.killstats.api_helper"


class Test_ApiHelper(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.request = RequestFactory()

        cls.user, _ = create_user_from_evecharacter(
            1001,
            permissions=["killstats.basic_access", "killstats.admin_access"],
        )

        cls.user2, _ = create_user_from_evecharacter(
            1002,
            permissions=[
                "killstats.basic_access",
            ],
        )

    def test_top10(self):
        request = self.request.get(reverse("killstats:index"))
        request.user = self.user
        response = get_top_10(
            request, month=7, year=2024, entity_type="corporation", entity_id=2001
        )

        expected_data = _api_helper.top10

        self.assertEqual(response, expected_data)

    def test_top10_alt(self):
        add_character_to_user(self.user, EveCharacter.objects.get(character_id=1004))
        request = self.request.get(reverse("killstats:index"))
        request.user = self.user
        response = get_top_10(
            request, month=7, year=2024, entity_type="alliance", entity_id=3001
        )

        expected_data = _api_helper.top10_alt

        self.assertEqual(response, expected_data)

    @patch(MODULE_PATH + ".EveEntity.objects.get")
    def test_get_top_10_does_not_exist(self, mock_get):
        mock_get.side_effect = EveEntity.DoesNotExist

        request = self.request.get(reverse("killstats:index"))
        request.user = self.user

        expected_data = _api_helper.top10_unknown

        response = get_top_10(
            request, month=7, year=2024, entity_type="corporation", entity_id=2001
        )
        self.assertEqual(response, expected_data)

    @patch(MODULE_PATH + ".EveEntity.objects.get")
    def test_get_top_10_attribute_error(self, mock_get):
        mock_get.side_effect = AttributeError

        request = self.request.get(reverse("killstats:index"))
        request.user = self.user

        result = get_top_10(
            request, month=7, year=2024, entity_type="corporation", entity_id=2001
        )

        expected_data = _api_helper.top10_unknown

        self.assertEqual(result, expected_data)
