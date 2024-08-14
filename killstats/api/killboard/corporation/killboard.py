"""API"""

# Standard Library
from typing import List

from ninja import NinjaAPI

# AA Killstats
from killstats.api import schema
from killstats.api.account_manager import AccountManager
from killstats.api.helpers import KillboardDate, get_corporations
from killstats.api.killboard_manager import (
    killboard_dashboard,
    killboard_hall,
    killboard_process_kills,
)
from killstats.hooks import get_extension_logger
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import CorporationsAudit

logger = get_extension_logger(__name__)


class KillboardCorporationApiEndpoints:
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
                Killmail.objects.prefetch_related("victim", "victim_ship")
                .filter(killmail_date__year=year)
                .order_by("-killmail_date")
            )

            killmail_filtered = killmail_year.filter_entities(corporations)

            killmail_month = killmail_filtered.filter(
                killmail_date__year=year,
                killmail_date__month=month,
            )

            kills, totalvalue, losses, totalvalue_loss = killboard_process_kills(
                killmail_month, corporations
            )

            date = KillboardDate(month, year)

            account = AccountManager(corporations=corporations)
            mains, _ = account.get_mains_alts()

            stats = killboard_dashboard(killmail_filtered, date, corporations)

            shame, fame = killboard_hall(killmail_month, corporations, mains)

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
            corporations = CorporationsAudit.objects.visible_to(request.user)

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
