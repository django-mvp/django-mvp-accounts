"""The demo's API: one endpoint that answers as whoever sent the token.

Kept apart from ``demo/views.py`` so the routes a project uses without
django-rest-knox can leave it out.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class WhoAmIView(APIView):
    """Say who the request's token belongs to."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return the email of the person the token was made for."""
        return Response({"email": request.user.email})
