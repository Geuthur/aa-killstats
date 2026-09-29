# Standard Library
from http import HTTPStatus

# Django
from django.urls import resolve, reverse

# AA Killstats
from killstats import views
from killstats.tests import AuthTestCase

MODULE_PATH = "killstats.views"


class TestViewKillstatsAccess(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_view_killboard_index(self):
        """Test view Killstats index."""
        # Test Data
        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user

        # Test Action
        response = views.killboard_index(request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_react_base_view(self):
        """Test React base view."""
        # Test Data
        request = self.factory.get(reverse("killstats:react_base"))
        request.user = self.user

        # Test Action
        response = views.react_base(request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_corporation_view(self):
        """Test Corporation View."""
        # Test Data
        request = self.factory.get(reverse("killstats:corporation", args=[2001]))
        request.user = self.user

        # Test Action
        response = views.corporation_view(request, 2001)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_alliance_view(self):
        """Test Alliance View."""
        # Test Data
        request = self.factory.get(reverse("killstats:alliance", args=[3001]))
        request.user = self.user

        # Test Action
        response = views.alliance_view(request, 3001)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_corporation_admin_view(self):
        """Test Corporation Overview."""
        # Test Data
        request = self.factory.get(reverse("killstats:corporation_admin"))
        request.user = self.user

        # Test Action
        response = views.corporation_admin(request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_alliance_admin_view(self):
        """Test Alliance Overview."""
        # Test Data
        request = self.factory.get(reverse("killstats:alliance_admin"))
        request.user = self.user

        # Test Action
        response = views.alliance_admin(request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_overview_corporations_route(self):
        """Test Overview Corporations route resolution."""
        # Test Data
        url = reverse("killstats:overview_corporations")

        # Test Action
        match = resolve(url)

        # Expected Result
        self.assertEqual(match.url_name, "overview_corporations")

    def test_overview_alliances_route(self):
        """Test Overview Alliances route resolution."""
        # Test Data
        url = reverse("killstats:overview_alliances")

        # Test Action
        match = resolve(url)

        # Expected Result
        self.assertEqual(match.url_name, "overview_alliances")

    def test_spa_catch_all_route_resolution(self):
        """Test that arbitrary client-side paths resolve to react_base."""
        # Test Data
        url = "/killstats/arbitrary/frontend/route/"

        # Test Action
        match = resolve(url)

        # Expected Result
        self.assertEqual(match.url_name, "react_base")

    def test_client_access_overview_and_spa(self):
        """Test client GET on overview and SPA routes returns 200 OK."""
        # Test Data
        self.client.force_login(self.user)

        # Test Action
        resp_corp_overview = self.client.get("/killstats/overview/corporations/")
        resp_alli_overview = self.client.get("/killstats/overview/alliances/")
        resp_root = self.client.get("/killstats/")

        # Expected Result
        self.assertEqual(resp_corp_overview.status_code, HTTPStatus.OK)
        self.assertEqual(resp_alli_overview.status_code, HTTPStatus.OK)
        self.assertEqual(resp_root.status_code, HTTPStatus.OK)
