"""The demo's routes without allauth's, for a project that does not install it."""

from django.urls import include, path

from demo.views import OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("", include("mvp.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

__all__ = ["urlpatterns"]
