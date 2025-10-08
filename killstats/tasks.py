"""App Tasks"""

# Third Party
from celery import chain as Chain
from celery import shared_task

# Django
from django.core.cache import cache
from django.db import IntegrityError

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Killstats
from killstats import __title__, app_settings
from killstats.decorators import when_esi_is_available
from killstats.helpers.killmail import KillmailBody
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

MAX_RETRIES_DEFAULT = 3

# Default params for all tasks.
TASK_DEFAULTS = {
    "time_limit": app_settings.KILLSTATS_TASKS_TIME_LIMIT,
    "timeout": app_settings.KILLSTATS_TASKS_TIMEOUT,
    "max_retries": MAX_RETRIES_DEFAULT,
}

# Default params for tasks that need run once only.
TASK_DEFAULTS_ONCE = {**TASK_DEFAULTS, **{"base": QueueOnce}}


@shared_task(**TASK_DEFAULTS_ONCE)
@when_esi_is_available
def run_zkb_redis():
    total_killmails = 0
    for _ in range(app_settings.KILLSTATS_MAX_KILLMAILS_PER_RUN):
        try:
            killmail = KillmailBody.create_from_zkb_redisq()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error fetching killmail from zKB RedisQ: %s", e)
            break

        if not cache.get(f"{__title__.upper()}_WORKER_SHUTDOWN") is None:
            logger.debug("Worker shutdown detected; stopping zKB RedisQ processing")
            break

        if not killmail:
            break

        killmail.save()

        corps_qs = CorporationsAudit.objects.all()
        allys_qs = AlliancesAudit.objects.all()

        for corporation in corps_qs:
            run_tracker_corporation.delay(
                corporation_id=corporation.corporation.corporation_id,
                killmail_id=killmail.id,
            )

        for alliance in allys_qs:
            run_tracker_alliance.delay(
                alliance_id=alliance.alliance.alliance_id, killmail_id=killmail.id
            )

        total_killmails += 1
    logger.info(
        "Killboard runs completed. %s killmails received from zKB",
        total_killmails,
    )


@shared_task(**TASK_DEFAULTS)
def run_tracker_corporation(corporation_id: int, killmail_id: int) -> None:
    """Run the tracker for the given killmail"""
    corporation = CorporationsAudit.objects.get(
        corporation__corporation_id=corporation_id
    )
    killmail = KillmailBody.get(killmail_id)
    killmail_new = corporation.process_killmail(killmail)
    if killmail_new:
        Chain(
            store_killmail.si(killmail.id),
        ).delay()
        logger.debug(
            "%s: Start storing killmail for %s",
            killmail.id,
            corporation.corporation.corporation_name,
        )


@shared_task(**TASK_DEFAULTS)
def run_tracker_alliance(alliance_id: int, killmail_id: int) -> None:
    """Run the tracker for the given killmail"""
    alliance = AlliancesAudit.objects.get(alliance__alliance_id=alliance_id)
    killmail = KillmailBody.get(killmail_id)
    killmail_new = alliance.process_killmail(killmail)
    if killmail_new:
        Chain(
            store_killmail.si(killmail.id),
        ).delay()
        logger.debug(
            "%s: Start storing killmail for %s",
            killmail.id,
            alliance.alliance.alliance_name,
        )


@shared_task(**TASK_DEFAULTS)
def store_killmail(killmail_id: int) -> None:
    """stores killmail as EveKillmail object"""
    killmail = KillmailBody.get(killmail_id)
    try:
        Killmail.objects.create_from_killmail(killmail)
    except IntegrityError:
        logger.warning(
            "%s: Failed to store killmail, because it already exists", killmail.id
        )
    else:
        logger.debug("%s: Stored killmail", killmail.id)
