from .alliance.killboard import KillboardAllianceApiEndpoints
from .corporation.killboard import KillboardCorporationApiEndpoints
from .corporation.stats import KillboardCorporationStatsApiEndpoints


def setup(api):
    KillboardCorporationApiEndpoints(api)
    KillboardAllianceApiEndpoints(api)
    KillboardCorporationStatsApiEndpoints(api)
