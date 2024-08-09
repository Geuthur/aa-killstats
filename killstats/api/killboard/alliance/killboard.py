"""API"""

# Standard Library
from typing import List

from ninja import NinjaAPI

# Django
from django.utils.translation import gettext_lazy as _

# AA Killstats
from killstats.api import schema
from killstats.api.account_manager import AccountManager
from killstats.api.helpers import KillboardDate, get_alliances
from killstats.api.killboard_manager import (
    killboard_dashboard,
    killboard_hall,
    killboard_process_kills,
)
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import AlliancesAudit

logger = get_extension_logger(__name__)


class KillboardAllianceApiEndpoints:
    tags = ["Killboard"]

    # pylint: disable=too-many-locals
    def __init__(self, api: NinjaAPI):
        @api.get(
            "killboard/month/{month}/year/{year}/alliance/{alliance_id}/",
            response={200: List[schema.KillboardIndex], 403: str},
            tags=self.tags,
        )
        # pylint: disable=duplicate-code
        def get_killstats(request, month, year, alliance_id: int):
            # Killboard
            if alliance_id == 0:
                alliances = get_alliances(request)
            else:
                alliances = [alliance_id]

            killmail_year = (
                Killmail.objects.select_related("victim", "victim_ship")
                .filter(killmail_date__year=year)
                .order_by("-killmail_date")
            )

            killmail_year = killmail_year.filter_alliances(alliances)

            killmail_month = killmail_year.filter(
                killmail_date__year=year,
                killmail_date__month=month,
            )

            account = AccountManager(alliances=alliances)
            mains, all_chars = account.get_mains_alts()

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
            "killboard/alliance/admin/",
            response={200: List[schema.AllianceAdmin], 403: str},
            tags=self.tags,
        )
        def get_corporation_admin(request):
            alliances = AlliancesAudit.objects.visible_to(request.user)

            if not alliances:
                return 403, "Permission Denied"

            alliance_dict = {}

            for alliance in alliances:
                # pylint: disable=broad-exception-caught
                try:
                    alliance_dict[alliance.alliance.alliance_id] = {
                        "alliance_id": alliance.alliance.alliance_id,
                        "alliance_name": alliance.alliance.alliance_name,
                    }
                except Exception:
                    continue

            output = []
            output.append({"alliance": alliance_dict})

            return output
