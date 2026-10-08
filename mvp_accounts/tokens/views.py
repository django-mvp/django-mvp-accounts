"""Prototype views behind the API tokens pages.

These exist so the screens can be looked at. They are untested and are
rebuilt once the screens are settled.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from knox.models import get_token_model
from knox.settings import knox_settings
from mvp.views import MVPTemplateView

from mvp_accounts.tokens.access import may_use_tokens
from mvp_accounts.tokens.forms import CreateTokenForm

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


def at_limit(user) -> bool:
    """Say whether the person holds as many tokens as the project allows."""
    limit = knox_settings.TOKEN_LIMIT_PER_USER
    return limit is not None and working_tokens(user).count() >= limit


class TokenPageMixin(LoginRequiredMixin):
    """Send a visitor to sign in, and refuse a person who may not use tokens."""

    def dispatch(self, request, *args, **kwargs):
        """Refuse a signed-in person the project has not let in."""
        if request.user.is_authenticated and not may_use_tokens(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TokensView(TokenPageMixin, MVPTemplateView):
    """List a person's tokens."""

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
        return super().get_context_data(
            tokens=working_tokens(self.request.user),
            token_limit=knox_settings.TOKEN_LIMIT_PER_USER,
            at_limit=at_limit(self.request.user),
            new_token=self.request.session.pop(JUST_CREATED, None),
            header_prefix=knox_settings.AUTH_HEADER_PREFIX,
            **kwargs,
        )


class CreateTokenView(TokenPageMixin, MVPTemplateView):
    """Ask for a lifetime, then create the token."""

    template_name = "mvp_accounts/tokens/create.html"
    page_title = _("Create a token")

    def get_breadcrumbs(self):
        """Lead back to the tokens page."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens"), "href": reverse("account_api_tokens")},
            {"text": _("Create")},
        ]

    def dispatch(self, request, *args, **kwargs):
        """Turn back a person who already holds as many tokens as allowed."""
        if (
            request.user.is_authenticated
            and may_use_tokens(request.user)
            and at_limit(request.user)
        ):
            messages.error(
                request,
                _(
                    "No token was created. You already hold as many as this site allows."
                ),
            )
            return redirect("account_api_tokens")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add the form, empty unless one was just refused."""
        kwargs.setdefault("form", CreateTokenForm())
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        """Create the token, or show the form again."""
        form = CreateTokenForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        instance, value = get_token_model().objects.create(
            user=request.user, expiry=form.get_expiry()
        )
        request.session[JUST_CREATED] = {
            "value": value,
            "digest": instance.digest,
        }
        return redirect("account_api_tokens")


class RevokeTokenView(TokenPageMixin, MVPTemplateView):
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
