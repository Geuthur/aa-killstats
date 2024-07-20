from django.test import RequestFactory, TestCase
from django.urls import reverse

from app_utils.testing import add_character_to_user, create_user_from_evecharacter

from killstats.api.helpers import get_corporations, get_main_and_alts_all
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

    def test_filter_loss_include(self):
        chars_in_losses = [1001, 1002]
        queryset = Killmail.objects.filter_loss(chars=chars_in_losses, exclude=False)
        for killmail in queryset:
            self.assertIn(killmail.victim.eve_id, chars_in_losses)

    def test_filter_loss_exclude(self):
        chars_not_in_losses = [1004, 1005]
        queryset = Killmail.objects.filter_loss(chars=chars_not_in_losses, exclude=True)
        for killmail in queryset:
            self.assertNotIn(killmail.victim.eve_id, chars_not_in_losses)

    def test_filter_kills(self):
        chars_in_kills = [2119686107]
        queryset = Killmail.objects.filter_kills(chars=chars_in_kills)
        for km in queryset:
            self.assertTrue(
                any(
                    attacker["character_id"] in chars_in_kills
                    for attacker in km.attackers
                )
            )

    def test_filter_kills_not_killed(self):
        chars_in_kills = [1234]
        queryset = Killmail.objects.filter_kills(chars=chars_in_kills)
        for km in queryset:
            self.assertTrue(
                any(
                    attacker["character_id"] in chars_in_kills
                    for attacker in km.attackers
                )
            )

    def test_filter_top_killer(self):
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user
        corporations = get_corporations(request)
        mains, _ = get_main_and_alts_all(corporations, char_ids=True)
        killmails = Killmail.objects.all()
        topkiller = killmails.filter_top_killer(mains)
        for char in topkiller:
            killmail_fame, _ = topkiller.get(char, (None, None))
            self.assertIsInstance(killmail_fame, Killmail)

    def test_filter_top_killer_alt(self):
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user
        corporations = get_corporations(request)
        mains, _ = get_main_and_alts_all(corporations, char_ids=True)
        killmails = Killmail.objects.all()
        topkiller = killmails.filter_top_killer(mains)
        for char in topkiller:
            killmail_fame, _ = topkiller.get(char, (None, None))
            self.assertIsInstance(killmail_fame, Killmail)

    def test_filter_top_killer_no_killer(self):
        self.user, self.character_ownership = create_user_from_evecharacter(
            1004,
        )
        request = self.factory.get(reverse("killstats:index"))
        request.user = self.user
        corporations = get_corporations(request)
        mains, _ = get_main_and_alts_all(corporations, char_ids=True)
        killmails = Killmail.objects.all()
        topkiller = killmails.filter_top_killer(mains)
        for char in topkiller:
            killmail_fame, _ = topkiller.get(char, (None, None))
            self.assertIsNone(killmail_fame)


class KillstatManagerTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.factory = RequestFactory()
