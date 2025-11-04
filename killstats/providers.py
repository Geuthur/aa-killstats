"""Shared ESI client for Voices of War."""

# Alliance Auth
from esi.openapi_clients import ESIClientProvider

# AA Killstats
from killstats import (
    __app_name_useragent__,
    __esi_compatibility_date__,
    __github_url__,
    __killmail_operations__,
    __version__,
)

esi = ESIClientProvider(
    compatibility_date=__esi_compatibility_date__,
    ua_appname=__app_name_useragent__,
    ua_version=__version__,
    ua_url=__github_url__,
    operations=__killmail_operations__,
)
