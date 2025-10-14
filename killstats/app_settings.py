"""App Settings"""

# Standard Library
import sys

# Alliance Auth (External Libs)
from app_utils.app_settings import clean_setting

IS_TESTING = sys.argv[1:2] == ["test"]

# Set Naming on Auth Hook
KILLSTATS_APP_NAME = clean_setting("KILLSTATS_APP_NAME", "Killstats")

# zKillboard - https://zkillboard.com/
ZKILLBOARD_BASE_URL = "https://zkillboard.com/"
ZKILLBOARD_API_URL = "https://zkillboard.com/api/"

ZKILLBOARD_BASE_URL_REGEX = r"^http[s]?:\/\/zkillboard\.com\/"
ZKILLBOARD_KILLMAIL_URL_REGEX = r"^http[s]?:\/\/zkillboard\.com\/kill\/\d+\/"

# Caching Key for Caching System
STORAGE_BASE_KEY = "killstats_storage_"

# Max lifetime of killmails in temporary storage in seconds
KILLSTATS_STORAGE_LIFETIME = clean_setting("KILLSTATS_STORAGE_LIFETIME", 3_600 * 24 * 3)

# Max Killmails per run should not be higher then 500
KILLSTATS_MAX_KILLMAILS_PER_RUN = clean_setting("KILLSTATS_MAX_KILLMAILS_PER_RUN", 200)

# Max lifetime of API Cache (10 min)
KILLSTATS_API_CACHE_LIFETIME = clean_setting("KILLSTATS_API_CACHE_LIFETIME", 10)

# Tasks max time limit in seconds
KILLSTATS_TASKS_TIME_LIMIT = clean_setting("KILLSTATS_TASKS_TIME_LIMIT", 1800)
# Tasks hard timeout
KILLSTATS_TASKS_TIMEOUT = clean_setting("KILLSTATS_TASKS_TIMEOUT", 600)

# Unique ID used to identify this server when fetching killmails from zKillboard
# Please note that the Queue ID is globally unique for all users of the zKillboard API
# Only use characters Example: "Gneuten9000"
KILLSTATS_QUEUE_ID = clean_setting("KILLSTATS_QUEUE_ID", "")

# Max duration to wait for new killmails from redisq in seconds
KILLSTATS_REDISQ_TTW = clean_setting("KILLSTATS_REDISQ_TTW", 5)

# Rate limiting for zKillboard RedisQ requests
# Max seconds to wait trying to acquire a rate slot (0 = don't wait)
KILLSTATS_REDISQ_RATE_TIMEOUT = clean_setting("KILLSTATS_REDISQ_RATE_TIMEOUT", 10)
# Maximum allowed requests per second across all workers/processes
KILLSTATS_REDISQ_MAX_PER_SEC = clean_setting("KILLSTATS_REDISQ_MAX_PER_SEC", 2)
