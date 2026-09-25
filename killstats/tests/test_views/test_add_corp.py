# Standard Library
from http import HTTPStatus
from unittest.mock import Mock, patch

# Django
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

# AA Killstats
from killstats.models.killstatsaudit import CorporationsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.utils import create_user_from_evecharacter
from killstats.views import (
    add_corp,
)

MODULE_PATH = "killstats.views"


@patch(MODULE_PATH + ".messages")
class KillstatsAuditTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()

        cls.factory = RequestFactory()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "killstats.basic_access",
                "killstats.admin_access",
            ],
        )
        char = cls.character_ownership.character
        char.corporation_id = 98000001
        char.corporation_name = "Player Corp"
        char.corporation_ticker = "PC"
        char.save()

    def _add_corporation(self, user, token):
        request = self.factory.get(reverse("killstats:add_corp"))
        request.user = user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        orig_view = add_corp.__wrapped__.__wrapped__.__wrapped__
        return orig_view(request, token)

    def test_add_corp_success(self, mock_messages):
        # given
        user = self.user
        token = user.token_set.get(character_id=1001)

        # when
        response = self._add_corporation(user, token)

        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response.url, reverse("killstats:corporation", args=[98000001])
        )
        self.assertEqual(mock_messages.info.call_count, 1)
        self.assertTrue(
            CorporationsAudit.objects.filter(
                corporation__corporation_id=98000001
            ).exists()
        )

    def test_add_corp_npc_corporation_rejected(self, mock_messages):
        # given
        user = self.user
        token = user.token_set.get(character_id=1001)
        char = self.character_ownership.character
        char.corporation_id = 1000125  # NPC Corporation (CONCORD)
        char.save()

        # when
        response = self._add_corporation(user, token)

        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertEqual(mock_messages.error.call_count, 1)
        self.assertFalse(
            CorporationsAudit.objects.filter(
                corporation__corporation_id=1000125
            ).exists()
        )
