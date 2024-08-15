from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from allianceauth.eveonline.evelinks import eveimageserver
from app_utils.testdata_factories import UserFactory

from killstats.admin import (
    AlliancesAuditAdmin,
    CorporationsAuditAdmin,
    clear_alliance_cache_zkb,
    clear_cache_zkb,
)
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.admin"


class MockRequest:
    pass


class TestKillstatsAuditAdmin(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.factory = RequestFactory()
        cls.site = AdminSite()
        cls.killstats_audit_admin = CorporationsAuditAdmin(CorporationsAudit, cls.site)
        cls.killstats_audit = CorporationsAudit.objects.get(id=1)

    def test_entity_pic(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        expected_html = '<img src="{}" class="img-circle">'.format(
            eveimageserver._eve_entity_image_url(
                "corporation", self.killstats_audit.corporation.corporation_id, 32
            )
        )
        self.assertEqual(
            self.killstats_audit_admin._entity_pic(self.killstats_audit),
            expected_html,
        )

    def test_corporation_corporation_id(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        self.assertEqual(
            self.killstats_audit_admin._corporation__corporation_id(
                self.killstats_audit
            ),
            2001,
        )

    def test_last_update(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        self.assertEqual(
            self.killstats_audit_admin._last_update(self.killstats_audit),
            self.killstats_audit.last_update,
        )

    def test_has_add_permission(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        self.assertFalse(self.killstats_audit_admin.has_add_permission(request))

    def test_has_change_permission(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        request = MockRequest()
        self.assertFalse(self.killstats_audit_admin.has_change_permission(request))
        self.assertFalse(
            self.killstats_audit_admin.has_change_permission(
                request, obj=self.killstats_audit
            )
        )

    @patch("killstats.admin.clear_cache_zkb")
    def test_clear_cache_for_selected(self, mock_clear_cache_zkb):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.post("/")
        request.user = user

        # Fügen Sie die MessageMiddleware hinzu
        session_middleware = SessionMiddleware(lambda req: None)
        message_middleware = MessageMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session = self.client.session
        message_middleware.process_request(request)

        queryset = CorporationsAudit.objects.filter(id=self.killstats_audit.pk)

        self.killstats_audit_admin.clear_cache_for_selected(request, queryset)

        mock_clear_cache_zkb.assert_called_once_with(
            self.killstats_audit.corporation.corporation_id
        )

        # Überprüfen, dass die Nachricht an den Benutzer gesendet wurde
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Cache successfully cleared for selected Corporations."
        )

    @patch(MODULE_PATH + ".get_redis_connection")
    def test_clear_cache_zkb(self, mock_get_redis_connection):
        # Mock the Redis connection
        mock_conn = MagicMock()
        mock_get_redis_connection.return_value = mock_conn

        # Mock the scan_iter method to return a list of keys
        mock_conn.scan_iter.return_value = [
            "zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345_1",
            "zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345_2",
            "zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345_3",
        ]

        # Call the function with a test corporation_id
        result = clear_cache_zkb(12345)

        # Verify that the delete method was called with the correct keys
        mock_conn.delete.assert_any_call(
            "zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345_1"
        )
        mock_conn.delete.assert_any_call(
            "zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345_2"
        )
        mock_conn.delete.assert_any_call(
            "zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345_3"
        )

        # Verify that the function returns True
        self.assertTrue(result)

        # Verify that scan_iter was called with the correct pattern
        mock_conn.scan_iter.assert_called_once_with(
            "*:zkb_page_cache_https://zkillboard.com/api/npc/0/corporationID/12345*"
        )


class TestAlliancesAuditAdmin(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.factory = RequestFactory()
        cls.site = AdminSite()
        cls.killstats_audit_admin = AlliancesAuditAdmin(AlliancesAudit, cls.site)
        cls.killstats_audit = AlliancesAudit.objects.get(id=1)

    def test_entity_pic(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        expected_html = '<img src="{}" class="img-circle">'.format(
            eveimageserver._eve_entity_image_url(
                "alliance", self.killstats_audit.alliance.alliance_id, 32
            )
        )
        self.assertEqual(
            self.killstats_audit_admin._entity_pic(self.killstats_audit),
            expected_html,
        )

    def test_alliance_alliance_id(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        self.assertEqual(
            self.killstats_audit_admin._alliance__alliance_id(self.killstats_audit),
            3001,
        )

    def test_last_update(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        self.assertEqual(
            self.killstats_audit_admin._last_update(self.killstats_audit),
            self.killstats_audit.last_update,
        )

    def test_has_add_permission(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        self.assertFalse(self.killstats_audit_admin.has_add_permission(request))

    def test_has_change_permission(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.get("/")
        request.user = user
        request = MockRequest()
        self.assertFalse(self.killstats_audit_admin.has_change_permission(request))
        self.assertFalse(
            self.killstats_audit_admin.has_change_permission(
                request, obj=self.killstats_audit
            )
        )

    @patch("killstats.admin.clear_alliance_cache_zkb")
    def test_clear_alliance_cache_for_selected(self, mock_clear_cache_zkb):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        request = self.factory.post("/")
        request.user = user

        # Fügen Sie die MessageMiddleware hinzu
        session_middleware = SessionMiddleware(lambda req: None)
        message_middleware = MessageMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session = self.client.session
        message_middleware.process_request(request)

        queryset = AlliancesAudit.objects.filter(id=self.killstats_audit.pk)

        self.killstats_audit_admin.clear_cache_for_selected(request, queryset)

        mock_clear_cache_zkb.assert_called_once_with(
            self.killstats_audit.alliance.alliance_id
        )

        # Überprüfen, dass die Nachricht an den Benutzer gesendet wurde
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Cache successfully cleared for selected Alliances."
        )

    @patch(MODULE_PATH + ".get_redis_connection")
    def test_clear_alliance_cache_zkb(self, mock_get_redis_connection):
        # Mock the Redis connection
        mock_conn = MagicMock()
        mock_get_redis_connection.return_value = mock_conn

        # Mock the scan_iter method to return a list of keys
        mock_conn.scan_iter.return_value = [
            "zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345_1",
            "zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345_2",
            "zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345_3",
        ]

        # Call the function with a test alliance_id
        result = clear_alliance_cache_zkb(12345)

        # Verify that the delete method was called with the correct keys
        mock_conn.delete.assert_any_call(
            "zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345_1"
        )
        mock_conn.delete.assert_any_call(
            "zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345_2"
        )
        mock_conn.delete.assert_any_call(
            "zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345_3"
        )

        # Verify that the function returns True
        self.assertTrue(result)

        # Verify that scan_iter was called with the correct pattern
        mock_conn.scan_iter.assert_called_once_with(
            "*:zkb_page_cache_https://zkillboard.com/api/npc/0/allianceID/12345*"
        )
