"""Shared ESI client for Voices of War."""

# Alliance Auth
from esi.clients import EsiClientProvider

# AA Killstats
from killstats import __version__

esi = EsiClientProvider(app_info_text=f"killstats v{__version__}")
