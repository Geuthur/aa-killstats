from ninja import NinjaAPI
from ninja.security import django_auth

from django.conf import settings

from killstats.api import killstats
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)

api = NinjaAPI(
    title="Killstats API",
    version="0.2.0",
    urls_namespace="killstats:new_api",
    auth=django_auth,
    csrf=True,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)

# Add the character endpoints
killstats.setup(api)
