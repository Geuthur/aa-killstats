"""App URLs"""

# Django
from django.urls import path, re_path

# AA Killstats
from killstats.api import api
from killstats.views import add_corp, corporation_admin, killboard_index

app_name: str = "killstats"

urlpatterns = [
    # Killstats
    path("index", killboard_index, {"corporation_pk": 0}, name="index"),
    path("corporation/<int:corporation_pk>/", killboard_index, name="corporation"),
    path("corporation_admin/", corporation_admin, name="corporation_admin"),
    # -- Killstats Audit
    path("add/", add_corp, name="add_corp"),
    # -- API System
    re_path(r"^api/", api.urls),
]
