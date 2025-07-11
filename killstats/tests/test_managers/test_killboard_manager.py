# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter
from eveuniverse.models import EveEntity, EveType

# AA Killstats
from killstats.models.killboard import Killmail
from killstats.tests.testdata.generate_killmail import create_killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse


class KillstatsManagerTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()
        cls.factory = RequestFactory()

        cls.killmail = create_killmail(
            killmail_id=1,
            killmail_date="2025-10-01T00:00:00Z",
            victim_corporation_id=2001,
            victim_alliance_id=3001,
            victim_region_id=1001,
            victim_solar_system_id=2001,
            victim_position_x=1.0,
            victim_position_y=1.0,
            victim_position_z=1.0,
            victim=EveEntity.objects.get(id=1001),
            victim_ship=EveType.objects.get(id=670),
            victim_total_value=1000,
            victim_fitted_value=500,
            victim_destroyed_value=500,
            victim_dropped_value=500,
        )

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
