from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EveEntity

from killstats.models.general import General

MODULE_PATH = "killstats.models.general"


class TestGeneralModel(TestCase):
    @classmethod
    def setUp(self):
        pass

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
