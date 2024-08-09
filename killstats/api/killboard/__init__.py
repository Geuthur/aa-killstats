from .alliance.killboard import KillboardAllianceApiEndpoints
from .corporation.killboard import KillboardCorporationApiEndpoints


def setup(api):
    KillboardCorporationApiEndpoints(api)
    KillboardAllianceApiEndpoints(api)
