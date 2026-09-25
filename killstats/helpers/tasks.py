# Standard Library
import time

# Third Party
import requests

# Django
from django.core.cache import cache

# AA Killstats
from killstats import USER_AGENT_TEXT
from killstats.app_settings import ZKILLBOARD_API_URL
from killstats.models import Killmail
from killstats.providers import logger


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def check_missing_killmails(
    corporation_id: int | None = None,
    alliance_id: int | None = None,
    pages: int = 3,
    delay_between_pages: float = 1.0,
) -> list[dict]:
    """
    Fetch up to `pages` from zKillboard for corporation_id and/or alliance_id and compare against database.
    Pre-caches missing killmails as KillmailBody objects.
    Returns summary, list of missing killmail IDs, and raw killmail data.
    """
    if not corporation_id and not alliance_id:
        raise ValueError("Either corporation_id or alliance_id must be provided.")

    path_parts = []
    if corporation_id:
        path_parts.append(f"corporationID/{corporation_id}")
    if alliance_id:
        path_parts.append(f"allianceID/{alliance_id}")

    base_path = "/".join(path_parts) + "/"

    all_killmail_ids = set()
    raw_killmails_by_id = {}
    pages_fetched = 0
    headers = {"User-Agent": USER_AGENT_TEXT, "Content-Type": "application/json"}

    for page in range(1, max(1, pages) + 1):
        if page > 1 and delay_between_pages > 0:
            time.sleep(delay_between_pages)

        try:
            url = f"{ZKILLBOARD_API_URL}{base_path}page/{page}/"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            zk_data = response.json()
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(
                "Error fetching zKillboard page %s in check_missing: %s",
                page,
                exc,
                exc_info=True,
            )
            break

        if not isinstance(zk_data, list) or not zk_data:
            break

        for km in zk_data:
            if isinstance(km, dict):
                km_id = (
                    km.get("killmail_id")
                    or km.get("killID")
                    or (km.get("killmail", {}).get("killmail_id"))
                )
                if km_id:
                    km_id = int(km_id)
                    all_killmail_ids.add(km_id)
                    raw_killmails_by_id[km_id] = km

        pages_fetched += 1

    existing_ids = set(
        Killmail.objects.filter(killmail_id__in=all_killmail_ids).values_list(
            "killmail_id", flat=True
        )
    )

    missing_ids = sorted(list(all_killmail_ids - existing_ids), reverse=True)
    missing_killmails = [
        raw_killmails_by_id[km_id]
        for km_id in missing_ids
        if km_id in raw_killmails_by_id
    ]
    return missing_killmails


def get_esi_killmail_bucket_remaining() -> int | None:
    """Return remaining tokens in django-esi 'killmail' bucket from cache, or None if not initialized."""
    val = cache.get("esi:bucket:killmail")
    if val is not None:
        try:
            return int(val)
        except (ValueError, TypeError):
            pass
    return None
