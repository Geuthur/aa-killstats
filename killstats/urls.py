"""App URLs"""

# Django
from django.urls import path, re_path

# AA Killstats
from killstats.api import api
from killstats.views import add_corp, killboard_index

app_name: str = "killstats"

urlpatterns = [
    # Killstats
    path("index", killboard_index, name="index"),
    # -- Killstats Audit
    path("add/", add_corp, name="add_corp"),
    # -- API System
    re_path(r"^api/", api.urls),
]
