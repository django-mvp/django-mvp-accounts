"""URL configuration for the demo project."""

from django.urls import include, path

from demo.views import OutboxView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("outbox/", OutboxView.as_view(), name="outbox"),
    path("accounts/", include("allauth.urls")),
    path("account/tokens/", include("mvp_accounts.tokens.urls")),
    path("", include("mvp.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]
