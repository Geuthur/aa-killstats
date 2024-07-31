"""API"""

# Standard Library
from typing import List

from ninja import NinjaAPI

# Django
from django.utils.translation import gettext_lazy as _

# AA Killstats
from killstats.api import schema
from killstats.api.helpers import get_corporations, get_main_and_alts_all
from killstats.api.killboard.killboard_manager import (
    killboard_dashboard,
    killboard_hall,
    killboard_process_kills,
)
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import KillstatsAudit

logger = get_extension_logger(__name__)


class KillboardDate:
    def __init__(self, month, year):
        self.month = int(month)
        self.year = int(year)


class KillboardApiEndpoints:
    tags = ["Killboard"]

    # pylint: disable=too-many-locals
    def __init__(self, api: NinjaAPI):
        @api.get(
            "killboard/month/{month}/year/{year}/corporation/{corporation_id}/",
            response={200: List[schema.KillboardIndex], 403: str},
            tags=self.tags,
        )
        def get_killstats(request, month, year, corporation_id: int):
            # Killboard
            if corporation_id == 0:
                corporations = get_corporations(request)
            else:
                corporations = [corporation_id]

            killmail_year = (
                Killmail.objects.select_related("victim", "victim_ship")
                .filter(killmail_date__year=year)
                .order_by("-killmail_date")
            )

            killmail_year = killmail_year.filter_corporations(corporations)

            killmail_month = killmail_year.filter(
                killmail_date__year=year,
                killmail_date__month=month,
            )

            mains, all_chars = get_main_and_alts_all(corporations)

            kills, totalvalue, losses, totalvalue_loss = killboard_process_kills(
                killmail_month, mains, all_chars
            )

            date = KillboardDate(month, year)

            stats = killboard_dashboard(killmail_year, date, mains, all_chars)

            shame, fame = killboard_hall(killmail_month, mains)

            output = []
            output.append(
                {
                    "kills": kills,
                    "losses": losses,
                    "totalKills": totalvalue,
                    "totalLoss": totalvalue_loss,
                    # Addons
                    "shame": shame,
                    "fame": fame,
                    "stats": stats,
                }
            )

            return output

        @api.get(
            "killboard/corporation/admin/",
            response={200: List[schema.CorporationAdmin], 403: str},
            tags=self.tags,
        )
        def get_corporation_admin(request):
            corporations = KillstatsAudit.objects.visible_to(request.user)

            if not corporations:
                return 403, "Permission Denied"

            corporation_dict = {}

            for corporation in corporations:
                # pylint: disable=broad-exception-caught
                try:
                    corporation_dict[corporation.corporation.corporation_id] = {
                        "corporation_id": corporation.corporation.corporation_id,
                        "corporation_name": corporation.corporation.corporation_name,
                    }
                except Exception:
                    continue

            output = []
            output.append({"corporation": corporation_dict})

            return output
