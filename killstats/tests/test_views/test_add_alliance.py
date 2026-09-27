# Standard Library
from http import HTTPStatus
from unittest.mock import Mock, patch

# Django
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import override_settings
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import (
    EveAllianceInfo,
)

# AA Killstats
from killstats.models.killstatsaudit import AlliancesAudit
from killstats.tests import AuthTestCase
from killstats.views import (
    add_alliance,
)

MODULE_PATH = "killstats.views"


@patch(MODULE_PATH + ".messages")
@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class KillstatsAllianceAuditTest(AuthTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def _add_alliance(self, user, token):
        request = self.factory.get(reverse("killstats:add_alliance"))
        request.user = user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        orig_view = add_alliance.__wrapped__.__wrapped__.__wrapped__
        return orig_view(request, token)

    @patch(MODULE_PATH + ".EveAllianceInfo.objects.get")
    def test_add_alliance(self, mock_alliance, mock_messages):
        # Test Data
        token = self.user.token_set.first()
        alliance = EveAllianceInfo.objects.create(
            alliance_id=9999,
            alliance_name="Test Alliance",
            alliance_ticker="TEST",
            executor_corp_id=8888,
        )
        mock_alliance.return_value = alliance
        mock_ally_data = Mock()
        mock_ally_data.id = 9999
        mock_ally_data.name = "Test Alliance"
        mock_ally_data.ticker = "TEST"
        mock_ally_data.executor_corp_id = 8888
        # Test Action
        response = self._add_alliance(self.user, token)
        # Expected Result
        alliance_audit = AlliancesAudit.objects.get(alliance__alliance_id=9999)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("killstats:alliance", args=[9999]))
        self.assertEqual(mock_messages.info.call_count, 1)
        self.assertEqual(alliance_audit.alliance.alliance_id, 9999)

    def test_add_alliance_npc_corporation_rejected(self, mock_messages):
        # Test Data
        token = self.user.token_set.first()
        char = self.user.profile.main_character
        char.corporation_id = 1000125  # NPC Corp
        char.save()
        # Test Action
        response = self._add_alliance(self.user, token)
        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertEqual(mock_messages.error.call_count, 1)
        self.assertFalse(
            AlliancesAudit.objects.filter(alliance__alliance_id=99000001).exists()
        )

    def test_add_alliance_no_alliance_rejected(self, mock_messages):
        # Test Data
        token = self.user.token_set.first()
        char = self.user.profile.main_character
        char.alliance_id = None
        char.save()
        # Test Action
        response = self._add_alliance(self.user, token)
        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertEqual(mock_messages.error.call_count, 1)
        self.assertFalse(
            AlliancesAudit.objects.filter(alliance__alliance_id=99000001).exists()
        )

    def test_add_alliance_npc_executor_rejected(self, mock_messages):
        # Test Data
        token = self.user.token_set.first()
        self.user.profile.main_character.alliance_id = 1_000_000
        self.user.profile.main_character.save()
        # Test Action
        response = self._add_alliance(self.user, token)
        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertEqual(mock_messages.error.call_count, 1)
        self.assertFalse(
            AlliancesAudit.objects.filter(alliance__alliance_id=1_000_000).exists()
        )
