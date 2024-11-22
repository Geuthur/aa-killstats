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
KILLBOARD_STORAGE_LIFETIME = clean_setting("KILLBOARD_STORAGE_LIFETIME", 3_600 * 24 * 3)

# Max Killmails per run should not be higher then 500
KILLBOARD_MAX_KILLMAILS_PER_RUN = clean_setting("KILLBOARD_MAX_KILLMAILS_PER_RUN", 400)

# Max lifetime of ZKB Request (1 day), Don't go lower then 1800 seconds
KILLBOARD_ZKB_CACHE_LIFETIME = clean_setting(
    "KILLBOARD_ZKB_CACHE_LIFETIME", 3_600 * 24 * 1
)

# Max lifetime of API Cache (10 min)
KILLBOARD_API_CACHE_LIFETIME = clean_setting("KILLBOARD_API_CACHE_LIFETIME", 10)

# Tasks hard timeout
KILLBOARD_TASKS_TIMEOUT = clean_setting("KILLBOARD_TASKS_TIMEOUT", 1_800)
