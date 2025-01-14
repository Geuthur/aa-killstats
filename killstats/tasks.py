"""App Tasks"""

from celery import chain as Chain
from celery import shared_task

# Django
from django.db import IntegrityError
from django.utils import timezone

from allianceauth.services.tasks import QueueOnce

# AA Killstatsp
from killstats import app_settings
from killstats.decorators import when_esi_is_available
from killstats.hooks import get_extension_logger
from killstats.managers.killboard_manager import KillmailManager
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit

logger = get_extension_logger(__name__)


@shared_task
@when_esi_is_available
def killmail_fetch_all(runs: int = 0):
    corps_query = CorporationsAudit.objects.all()
    allys_query = AlliancesAudit.objects.all()
    for corp in corps_query:
        killmail_update_corp.apply_async(args=[corp.corporation.corporation_id])
        runs = runs + 1
    for ally in allys_query:
        killmail_update_ally.apply_async(args=[ally.alliance.alliance_id])
        runs = runs + 1
    logger.info("Queued %s Killstats Audit Updates", runs)


# pylint: disable=unused-argument
@shared_task(bind=True, base=QueueOnce)
@when_esi_is_available
def killmail_update_corp(self, corp_id: int, runs: int = 0):
    """Updates the killmails for a corporation"""
    corp = CorporationsAudit.objects.get(corporation__corporation_id=corp_id)
    killstats_url = f"https://zkillboard.com/api/npc/0/corporationID/{corp.corporation.corporation_id}/"

    killmail_list = KillmailManager.get_killmail_data_bulk(killstats_url)
    existing_kms = Killmail.objects.all().values_list("killmail_id", flat=True)
    if killmail_list:
        for killmail_dict in killmail_list:
            killmail = KillmailManager._create_from_dict(killmail_dict)
            killmail.save()
            if killmail.id in existing_kms:
                continue
            runs = runs + (1 if killmail else 0)
            Chain(
                store_killmail.si(killmail.id),
            ).delay()
        corp.last_update = timezone.now()
        corp.save()

    if not runs == 0:
        logger.info(
            "Killboard runs completed. %s killmails received from zKB for %s",
            runs,
            corp.corporation.corporation_name,
        )
    else:
        logger.debug("No new Killmail found.")


# pylint: disable=unused-argument
@shared_task(bind=True, base=QueueOnce)
@when_esi_is_available
def killmail_update_ally(self, alliance_id: int, runs: int = 0):
    """Updates the killmails for a corporation"""
    ally = AlliancesAudit.objects.get(alliance__alliance_id=alliance_id)
    killstats_url = (
        f"https://zkillboard.com/api/npc/0/allianceID/{ally.alliance.alliance_id}/"
    )

    killmail_list = KillmailManager.get_killmail_data_bulk(killstats_url)

    existing_kms = Killmail.objects.all().values_list("killmail_id", flat=True)

    if killmail_list:
        for killmail_dict in killmail_list:
            killmail = KillmailManager._create_from_dict(killmail_dict)
            killmail.save()
            if killmail.id in existing_kms:
                continue
            runs = runs + (1 if killmail else 0)
            Chain(
                store_killmail.si(killmail.id),
            ).delay()
        ally.last_update = timezone.now()
        ally.save()

    if not runs == 0:
        logger.info(
            "Killboard runs completed. %s killmails received from zKB for %s",
            runs,
            ally.alliance.alliance_name,
        )
    else:
        logger.debug("No new Killmail found.")


@shared_task(timeout=app_settings.KILLBOARD_TASKS_TIMEOUT)
def store_killmail(killmail_id: int) -> None:
    """stores killmail as EveKillmail object"""
    killmail = KillmailManager.get(killmail_id)
    try:
        Killmail.objects.create_from_killmail(killmail)
    except IntegrityError:
        logger.warning(
            "%s: Failed to store killmail, because it already exists", killmail.id
        )
    else:
        logger.debug("%s: Stored killmail", killmail.id)
