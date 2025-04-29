"""App Settings"""

# Alliance Auth (External Libs)
from app_utils.app_settings import clean_setting

# Set Naming on Auth Hook
KILLSTATS_APP_NAME = clean_setting("KILLSTATS_APP_NAME", "Killstats")

# If True you need to set up the Logger
KILLSTATS_LOGGER_USE = clean_setting("KILLSTATS_LOGGER_USE", False)

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

# Tasks hard timeout
KILLSTATS_TASKS_TIMEOUT = clean_setting("KILLSTATS_TASKS_TIMEOUT", 1_800)

# Unique ID used to identify this server when fetching killmails from zKillboard
# Please note that the Queue ID is globally unique for all users of the zKillboard API
# Only use characters Example: "Gneuten9000"
KILLSTATS_QUEUE_ID = clean_setting("KILLSTATS_QUEUE_ID", "")

# Max duration to wait for new killmails from redisq in seconds
KILLSTATS_REDISQ_TTW = clean_setting("KILLSTATS_REDISQ_TTW", 5)

# Timeout for Lock to ensure atomic access to ZKB RedisQ
KILLSTATS_REDISQ_LOCK_TIMEOUT = clean_setting("KILLSTATS_REDISQ_LOCK_TIMEOUT", 5)
