"""App Signals"""

# Third Party
from celery import signals

# Django
from django.core.cache import cache

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Killstats
from killstats import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@signals.worker_ready.connect
def worker_ready_handler(sender, **kwargs):  # pylint: disable=unused-argument
    """Handle worker ready signal.

    This signal is sent when a Celery worker is fully started and ready to
    accept tasks. We use this signal to clear any existing shutdown flag in
    the cache, ensuring that the system is marked as active and ready to
    process tasks.
    """
    cache.delete(f"{__title__.upper()}_WORKER_SHUTDOWN")
    logger.debug("Worker ready signal successfully processed for %s", sender)


@signals.worker_shutting_down.connect
def worker_shutting_down_handler(sender, **kwargs):  # pylint: disable=unused-argument
    """Handle worker shutdown signal.

    Celery sends this signal when a worker is in the process of shutting down.
    We use this signal to set a shutdown flag in the cache, which can be checked
    by long-running tasks to gracefully stop processing new items. This helps
    ensure that tasks do not start new work when the worker is shutting down.
    """
    cache.set(f"{__title__.upper()}_WORKER_SHUTDOWN", True, timeout=120)
    logger.debug("Worker shutting down signal successfully processed for %s", sender)
