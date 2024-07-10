from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from killstats.models.general import EveEntity, General

MODULE_PATH = "killstats.models.general"


class TestGeneralModel(TestCase):
    @classmethod
    def setUp(self):
        self.eveentity = EveEntity()
        self.eveentity.name = "Test"
        self.eveentity.eve_id = 123
        self.eveentity.category = "Test Category"
        self.eveentity.last_update = timezone.now() - timedelta(days=8)

    def test_basic_permission(self):
        # given
        permission = Permission.objects.select_related("content_type").get(
            content_type__app_label="killstats", codename="basic_access"
        )
        # when
        self.assertEqual(General.basic_permission(), permission)

    def test_users_with_basic_access(self):
        with patch(
            MODULE_PATH + ".users_with_permission"
        ) as mock_users_with_permission:
            mock_users_with_permission.return_value = "Test"
            self.assertEqual(General.users_with_basic_access(), "Test")

    def test_str(self):
        self.assertEqual(str(self.eveentity), "Test")

    def test_repr(self):
        self.assertEqual(
            repr(self.eveentity),
            "EveEntity(id=123, category='Test Category', name='Test')",
        )

    def test_is_alliance(self):
        self.eveentity.category = self.eveentity.CATEGORY_ALLIANCE
        self.assertTrue(self.eveentity.is_alliance)

    def test_is_corporation(self):
        self.eveentity.category = self.eveentity.CATEGORY_CORPORATION
        self.assertTrue(self.eveentity.is_corporation)

    def test_is_character(self):
        self.eveentity.category = self.eveentity.CATEGORY_CHARACTER
        self.assertTrue(self.eveentity.is_character)

    @patch(
        MODULE_PATH + ".EveAllianceInfo.generic_logo_url"
    )  # replace with your actual module path
    def test_icon_url_alliance(self, mock_generic_logo_url):
        self.eveentity.category = self.eveentity.CATEGORY_ALLIANCE
        mock_generic_logo_url.return_value = "Test URL"
        self.assertEqual(self.eveentity.icon_url(), "Test URL")

    @patch(
        MODULE_PATH + ".EveCorporationInfo.generic_logo_url"
    )  # replace with your actual module path
    def test_icon_url_corporation(self, mock_generic_logo_url):
        self.eveentity.category = self.eveentity.CATEGORY_CORPORATION
        mock_generic_logo_url.return_value = "Test URL"
        self.assertEqual(self.eveentity.icon_url(), "Test URL")

    @patch(
        MODULE_PATH + ".EveCharacter.generic_portrait_url"
    )  # replace with your actual module path
    def test_icon_url_character(self, mock_generic_portrait_url):
        self.eveentity.category = self.eveentity.CATEGORY_CHARACTER
        mock_generic_portrait_url.return_value = "Test URL"
        self.assertEqual(self.eveentity.icon_url(), "Test URL")

    def test_icon_url_not_implemented(self):
        self.eveentity.category = "Invalid Category"
        with self.assertRaises(NotImplementedError):
            self.eveentity.icon_url()
