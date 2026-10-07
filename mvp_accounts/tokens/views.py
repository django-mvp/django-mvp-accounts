"""Prototype views behind the API tokens page.

These exist so the screens can be looked at. They are untested and are
rebuilt once the screens are settled.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from knox.models import get_token_model
from knox.settings import knox_settings
from mvp.views import MVPTemplateView

# Where the prototype keeps a new token between creating it and showing it.
JUST_CREATED = "mvp_accounts_just_created"


def working_tokens(user):
    """Return the person's tokens that have not expired, newest first."""
    return (
        get_token_model()
        .objects.filter(user=user)
        .filter(Q(expiry__isnull=True) | Q(expiry__gt=timezone.now()))
        .order_by("-created")
    )


class TokensView(LoginRequiredMixin, MVPTemplateView):
    """List a person's tokens, and create one."""

    template_name = "mvp_accounts/tokens/list.html"
    page_title = _("API tokens")
    page_subtitle = _(
        "A token lets a script or another tool use the API as you, "
        "without your password."
    )

    def get_breadcrumbs(self):
        """Lead back to the Account Center."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens")},
        ]

    def get_context_data(self, **kwargs):
        """Add the tokens, the limit and a token created a moment ago."""
        tokens = working_tokens(self.request.user)
        limit = knox_settings.TOKEN_LIMIT_PER_USER
        return super().get_context_data(
            tokens=tokens,
            token_limit=limit,
            at_limit=limit is not None and tokens.count() >= limit,
            new_token=self.request.session.pop(JUST_CREATED, None),
            header_prefix=knox_settings.AUTH_HEADER_PREFIX,
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        """Create a token, unless the person already holds as many as allowed."""
        limit = knox_settings.TOKEN_LIMIT_PER_USER
        if limit is not None and working_tokens(request.user).count() >= limit:
            messages.error(
                request,
                _(
                    "No token was created. You already hold as many as this site allows."
                ),
            )
            return redirect("account_api_tokens")
        instance, value = get_token_model().objects.create(user=request.user)
        request.session[JUST_CREATED] = {
            "value": value,
            "digest": instance.digest,
        }
        return redirect("account_api_tokens")


class RevokeTokenView(LoginRequiredMixin, MVPTemplateView):
    """Ask before revoking one token, then delete it."""

    template_name = "mvp_accounts/tokens/revoke.html"
    page_title = _("Revoke this token?")

    def get_breadcrumbs(self):
        """Lead back to the tokens page."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens"), "href": reverse("account_api_tokens")},
            {"text": _("Revoke")},
        ]

    def get_token(self):
        """Return the person's own token, or answer as if there were none."""
        return get_object_or_404(
            working_tokens(self.request.user), digest=self.kwargs["digest"]
        )

    def get_context_data(self, **kwargs):
        """Add the token being revoked."""
        return super().get_context_data(token=self.get_token(), **kwargs)

    def post(self, request, *args, **kwargs):
        """Delete the token and say so."""
        token = self.get_token()
        token_key = token.token_key
        token.delete()
        messages.success(
            request, _("Token %(token)s… was revoked.") % {"token": token_key}
        )
        return redirect("account_api_tokens")
