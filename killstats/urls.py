"""App URLs"""

# Django
from django.urls import path, re_path

# AA Killstats
from killstats.api import api
from killstats.views import (
    add_alliance,
    add_corp,
    alliance_admin,
    corporation_admin,
    killboard_index,
)

app_name: str = "killstats"

urlpatterns = [
    # Killstats
    path("index", killboard_index, {"corporation_pk": 0}, name="index"),
    path("corporation/<int:corporation_pk>/", killboard_index, name="corporation"),
    path("alliance/<int:alliance_pk>/", killboard_index, name="alliance"),
    path("corporation_admin/", corporation_admin, name="corporation_admin"),
    path("alliance_admin/", alliance_admin, name="alliance_admin"),
    # -- Killstats Audit
    path("add_corp/", add_corp, name="add_corp"),
    path("add_alliance/", add_alliance, name="add_alliance"),
    # -- API System
    re_path(r"^api/", api.urls),
]
