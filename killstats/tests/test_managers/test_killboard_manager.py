from django.test import RequestFactory, TestCase
from django.urls import reverse

from app_utils.testing import create_user_from_evecharacter

from killstats.api.account_manager import AccountManager
from killstats.api.helpers import get_corporations
from killstats.models.killboard import Killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all


class KillstatManagerQuerySetTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.factory = RequestFactory()

    def test_visible_to_superuser(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        self.user.is_superuser = True
        self.user.save()
        # when
        result = Killmail.objects.visible_to(self.user)
        expected_result = Killmail.objects.all()
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_visible_to_admin_access(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "killstats.admin_access",
            ],
        )
        # when
        expected_result = Killmail.objects.all()
        result = Killmail.objects.visible_to(self.user)
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_visible_to_no_access(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        # when
        expected_result = []
        result = Killmail.objects.visible_to(self.user)
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_filter_structure_exclude_false(self):
        queryset = Killmail.objects.filter_structure(exclude=False)
        expected_count = Killmail.objects.filter(
            victim_ship__eve_group__eve_category_id=65
        ).count()
        self.assertEqual(queryset.count(), expected_count)

    def test_filter_structure_exclude_true(self):
        queryset = Killmail.objects.filter_structure(exclude=True)
        expected_count = Killmail.objects.exclude(
            victim_ship__eve_group__eve_category_id=65
        ).count()
        self.assertEqual(queryset.count(), expected_count)


class KillstatManagerTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.factory = RequestFactory()
