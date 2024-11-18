from http import HTTPStatus
from unittest.mock import Mock, patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from esi.models import Token

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from app_utils.testing import create_user_from_evecharacter

from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.views import (
    add_alliance,
    add_corp,
    alliance_admin,
    corporation_admin,
    killboard_index,
)

MODULE_PATH = "killstats.views"


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

    def test_view(self):
        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user
        response = killboard_index(request, 0)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_single(self):
        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user
        response = killboard_index(request, 20000001)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_corporation_admin(self):
        request = self.factory.get(reverse("killstats:corporation_admin"))
        request.user = self.user
        response = corporation_admin(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_alliance_admin(self):
        request = self.factory.get(reverse("killstats:alliance_admin"))
        request.user = self.user
        response = alliance_admin(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch(MODULE_PATH + ".messages")
    @patch(MODULE_PATH + ".killmail_update_corp")
    def test_add_corp(self, mock_update_corp, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = self.character_ownership.character.character_id
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker
        request = self.factory.get(reverse("killstats:add_corp"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_corp.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertTrue(mock_messages.info.called)
        self.assertTrue(mock_update_corp.apply_async.called)
        self.assertTrue(
            CorporationsAudit.objects.get(
                corporation=self.character_ownership.character.corporation
            )
        )

    @patch(MODULE_PATH + ".messages")
    @patch(MODULE_PATH + ".killmail_update_corp")
    def test_add_corp_not_created(self, mock_update_corp, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = self.character_ownership.character.character_id
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker

        corp, _ = EveCorporationInfo.objects.get_or_create(
            corporation_id=token.corporation_id,
            defaults={
                "member_count": 0,
                "corporation_ticker": token.corporation_ticker,
                "corporation_name": token.corporation_name,
            },
        )
        CorporationsAudit.objects.update_or_create(
            corporation=corp, owner=self.character_ownership.character
        )

        request = self.factory.get(reverse("killstats:add_corp"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_corp.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertTrue(mock_messages.info.called)
        self.assertFalse(mock_update_corp.apply_async.called)
        self.assertTrue(
            CorporationsAudit.objects.get(
                corporation=self.character_ownership.character.corporation
            )
        )

    @patch(MODULE_PATH + ".messages")
    def test_add_corp_char_not_found(self, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = 999999
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker

        request = self.factory.get(reverse("killstats:add_corp"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_corp.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        mock_messages.error.assert_called_once()


class KillstatsAllianceAuditTest(TestCase):
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

    @patch(MODULE_PATH + ".messages")
    @patch(MODULE_PATH + ".killmail_update_corp")
    def test_add_alliance(self, mock_update_corp, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = self.character_ownership.character.character_id
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker
        request = self.factory.get(reverse("killstats:add_alliance"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_alliance.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertTrue(mock_messages.info.called)
        # self.assertTrue(mock_update_corp.apply_async.called)
        self.assertTrue(
            AlliancesAudit.objects.get(
                alliance=self.character_ownership.character.alliance
            )
        )

    @patch(MODULE_PATH + ".messages")
    @patch(MODULE_PATH + ".killmail_update_corp")
    @patch(MODULE_PATH + ".EveAllianceInfo.objects.get")
    def test_add_alliance_none(self, mock_alliance, mock_update_corp, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = self.character_ownership.character.character_id
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker
        mock_alliance.return_value = None

        request = self.factory.get(reverse("killstats:add_alliance"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_alliance.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertTrue(mock_messages.error.called)

    @patch(MODULE_PATH + ".messages")
    @patch(MODULE_PATH + ".killmail_update_corp")
    @patch(MODULE_PATH + ".EveAllianceInfo.objects.create_alliance")
    @patch(MODULE_PATH + ".EveAllianceInfo.objects.get")
    def test_add_alliance_not_exist(
        self, mock_alliance, mock_alliance_create, mock_update_corp, mock_messages
    ):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = self.character_ownership.character.character_id
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker

        mock_alliance.side_effect = EveAllianceInfo.DoesNotExist
        mock_alliance_create.return_value = EveAllianceInfo(
            alliance_id=3999,
            alliance_name="Test Corp",
            alliance_ticker="TC",
            executor_corp_id=2999,
        )
        mock_alliance_create.return_value.save()

        request = self.factory.get(reverse("killstats:add_alliance"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_alliance.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertTrue(mock_messages.info.called)

    @patch(MODULE_PATH + ".messages")
    @patch(MODULE_PATH + ".killmail_update_corp")
    def test_add_alliance_not_created(self, mock_update_corp, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = self.character_ownership.character.character_id
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker

        ally = EveAllianceInfo.objects.get(
            alliance_id=30000001,
        )
        AlliancesAudit.objects.update_or_create(
            alliance=ally, owner=self.character_ownership.character
        )

        request = self.factory.get(reverse("killstats:add_alliance"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_alliance.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        self.assertTrue(mock_messages.info.called)
        self.assertFalse(mock_update_corp.apply_async.called)
        self.assertTrue(
            AlliancesAudit.objects.get(
                alliance=self.character_ownership.character.alliance
            )
        )

    @patch(MODULE_PATH + ".messages")
    def test_add_alliance_char_not_found(self, mock_messages):
        self.client.force_login(self.user)
        token = Mock(spec=Token)
        token.character_id = 999999
        token.corporation_id = self.character_ownership.character.corporation_id
        token.corporation_name = self.character_ownership.character.corporation_name
        token.corporation_ticker = self.character_ownership.character.corporation_ticker

        request = self.factory.get(reverse("killstats:add_alliance"))
        request.user = self.user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        # given
        orig_view = add_alliance.__wrapped__.__wrapped__
        # when
        response = orig_view(request, token)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("killstats:index"))
        mock_messages.error.assert_called_once()
