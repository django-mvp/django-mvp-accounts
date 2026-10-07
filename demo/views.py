"""The demo project's pages."""

from django.conf import settings
from django.http import Http404
from mvp.views import MVPTemplateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from demo.models import SentMessage


class OverviewView(MVPTemplateView):
    """What this package is, and what it puts on a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "What this package puts on a page"
    breadcrumbs = [{"text": "Overview"}]


class OutboxView(MVPTemplateView):
    """What the demo would have sent, newest first.

    Only exists with DEBUG on. It shows sign-in codes and password reset links
    to anyone who opens it, which is the point in a demo and nowhere else.
    """

    template_name = "demo/outbox.html"
    page_title = "Outbox"
    page_subtitle = "The emails and text messages the demo would have sent"
    breadcrumbs = [{"text": "Outbox"}]

    def dispatch(self, request, *args, **kwargs):
        """Hide the outbox unless DEBUG is on."""
        if not settings.DEBUG:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add the twenty newest messages."""
        return super().get_context_data(
            messages_sent=SentMessage.objects.all()[:20], **kwargs
        )


class WhoAmIView(APIView):
    """Answer with the person a token belongs to.

    The one endpoint of the demo's API. It is there so a token made on the API
    tokens page can be tried against a real request.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Name the person the request was authenticated as."""
        return Response({"email": request.user.email})
