"""The suite's urlconf.

It is the demo project's routes plus whatever a test needs a route for. A
test-only view is added here rather than in ``demo/urls.py``, so the demo
project keeps only the pages a person is meant to open.
"""

from allauth.account.decorators import verified_email_required
from django.http import HttpResponse
from django.urls import path

from demo.urls import urlpatterns as demo_urlpatterns


@verified_email_required
def members_only(request):
    """A page that asks for a verified address, as a host project's might."""
    return HttpResponse("members only")


urlpatterns = [
    *demo_urlpatterns,
    path("members-only/", members_only, name="members_only"),
]

__all__ = ["urlpatterns"]
