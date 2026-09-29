"""App URLs"""

# Django
from django.urls import path, re_path

# AA Killstats
from killstats import views
from killstats.api import api

app_name: str = "killstats"  # pylint: disable=invalid-name

urlpatterns = [
    # -- API System (excluded from catch-all)
    re_path(r"^api/", api.urls),
    # -- Killstats Audit
    path("add_corp/", views.add_corp, name="add_corp"),
    path("add_alliance/", views.add_alliance, name="add_alliance"),
    # -- Named routes for backwards compatibility
    path("index", views.killboard_index, name="index"),
    path(
        "corporation/<int:corporation_id>/", views.corporation_view, name="corporation"
    ),
    path("alliance/<int:alliance_id>/", views.alliance_view, name="alliance"),
    path("corporation_admin/", views.corporation_admin, name="corporation_admin"),
    path("alliance_admin/", views.alliance_admin, name="alliance_admin"),
    path(
        "overview/corporations/",
        views.corporation_admin,
        name="overview_corporations",
    ),
    path(
        "overview/alliances/",
        views.alliance_admin,
        name="overview_alliances",
    ),
    # -- React Frontend (V2)
    path(
        "v2/corporation/<int:corporation_id>/",
        views.react_corporation_view,
        name="react_corporation",
    ),
    path(
        "v2/alliance/<int:alliance_id>/",
        views.react_alliance_view,
        name="react_alliance",
    ),
    # -- Catch-all / React Frontend SPA routing (handles F5 refresh on client-side routes)
    re_path(
        r"^(?!api/|add_corp|add_alliance).*$",
        views.react_base,
        name="react_base",
    ),
]
