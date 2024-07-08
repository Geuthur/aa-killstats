from unittest.mock import MagicMock

from django.test import TestCase
from django.urls import reverse

from app_utils.testdata_factories import UserMainFactory

from killstats.auth_hooks import KillstatsMenuItem


class TestAuthHooks(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = UserMainFactory(permissions=["killstats.basic_access"])
        cls.html_menu = f"""
            <li class="d-flex flex-wrap m-2 p-2 pt-0 pb-0 mt-0 mb-0 me-0 pe-0">
                <i class="nav-link fas fa-star fa-fw fa-fw align-self-center me-3 active"></i>
                <a class="nav-link flex-fill align-self-center me-auto active" href="{reverse('killstats:index')}">
                    Killstats
                </a>
            </li>
        """

    def test_menu_hook(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("killstats:index"))

        self.assertContains(response, self.html_menu, html=True)

    def test_render_returns_empty_string_for_user_without_permission(self):
        # given
        killstats_menu_item = KillstatsMenuItem()
        mock_request = MagicMock()
        mock_request.user.has_perm.return_value = False

        # when
        result = killstats_menu_item.render(mock_request)
        # then
        self.assertEqual(
            result,
            "",
            "Expected render method to return an empty string for users without permission",
        )
