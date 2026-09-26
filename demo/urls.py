from django.urls import include, path

from demo.views import OutboxView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    # What the demo would have emailed or texted: codes and links.
    path("outbox/", OutboxView.as_view(), name="outbox"),
    # Sign-in, sign-up and the rest of allauth's account pages.
    path("accounts/", include("allauth.urls")),
    # The application shell's own routes, the Account Center among them.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
