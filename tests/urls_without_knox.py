"""The demo's routes without the tokens pages, for a project that never routes them."""

from django.urls import include, path

from demo.views import OutboxView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("outbox/", OutboxView.as_view(), name="outbox"),
    path("accounts/", include("allauth.urls")),
    path("", include("mvp.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

__all__ = ["urlpatterns"]
