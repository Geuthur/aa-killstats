# Standard Library
import sys
import time
from functools import wraps

# Alliance Auth (External Libs)
from app_utils.esi import EsiDailyDowntime, fetch_esi_status

from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)

# True when tests are currently running, else False.
IS_TESTING = sys.argv[1:2] == ["test"]


def when_esi_is_available(func):
    """Make sure the decorated task only runs when esi is available.

    Raise exception when ESI is offline.
    Complete the task without running it when downtime is detected.

    Automatically disabled during tests.
    """

    @wraps(func)
    def outer(*args, **kwargs):
        if IS_TESTING is not True:
            try:
                fetch_esi_status().raise_for_status()
            except EsiDailyDowntime:
                logger.info("Daily Downtime detected. Aborting.")
                return None  # function will not run

        return func(*args, **kwargs)

    return outer


def log_timing(logs):
    """
    Ein Dekorator, der die Ausführungszeit einer Funktion misst und in die Logdatei schreibt.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 3)
            logs.debug(
                "TIME: %s run for %s seconds with args: %s",
                func.__name__,
                elapsed_time,
                args,
            )
            return result

        return wrapper

    return decorator
