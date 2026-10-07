"""URL configuration for the demo project."""

from django.urls import include, path

from demo.views import OutboxView, OverviewView, WhoAmIView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("outbox/", OutboxView.as_view(), name="outbox"),
    path("accounts/", include("allauth.urls")),
    # Ahead of django-mvp's own routes, which also sit under account/.
    path("account/tokens/", include("mvp_accounts.tokens.urls")),
    path("api/whoami/", WhoAmIView.as_view(), name="api-whoami"),
    path("", include("mvp.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]
