"""App URLs"""

# Django
from django.urls import path, re_path

from killstats import views

# AA Killstats
from killstats.api import api

app_name: str = "killstats"

urlpatterns = [
    # Killstats
    path("index", views.killboard_index, name="index"),
    path(
        "corporation/<int:corporation_id>/", views.corporation_view, name="corporation"
    ),
    path("alliance/<int:alliance_id>/", views.alliance_view, name="alliance"),
    path("corporation_admin/", views.corporation_admin, name="corporation_admin"),
    path("alliance_admin/", views.alliance_admin, name="alliance_admin"),
    # -- Killstats Audit
    path("add_corp/", views.add_corp, name="add_corp"),
    path("add_alliance/", views.add_alliance, name="add_alliance"),
    # -- API System
    re_path(r"^api/", api.urls),
]
