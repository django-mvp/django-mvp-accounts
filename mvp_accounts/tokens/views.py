"""The API tokens pages: a person's list, a create form and a revoke confirmation.

Only a project that routes ``mvp_accounts.tokens.urls`` ever imports this module,
which is why it may import django-rest-knox where nothing else in the package may.
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from knox.models import get_token_model
from knox.settings import knox_settings
from mvp.views import MVPTemplateView
from mvp.views.base import PageMixin

from mvp_accounts.tokens.forms import CreateTokenForm


class TokenPageMixin(UserPassesTestMixin):
    """Let a signed-in person in and send a visitor to sign in.

    Django's ``UserPassesTestMixin`` redirects an anonymous visitor to sign in
    and refuses a signed-in person whose ``test_func`` fails.
    """

    request: HttpRequest

    def test_func(self) -> bool:
        """Say whether the person may use the tokens pages."""
        return bool(self.request.user.is_authenticated)

    def get_working_tokens(self) -> QuerySet:
        """Return the signed-in person's tokens that have not expired, newest first.

        Every page starts from this, so none can reach another person's token
        or one that has expired.

        Returns:
            The person's tokens with no expiry or an expiry in the future.
        """
        tokens: QuerySet = (
            get_token_model()
            .objects.filter(user=self.request.user)
            .filter(Q(expiry__isnull=True) | Q(expiry__gt=timezone.now()))
            .order_by("-created")
        )
        return tokens

    def is_at_limit(self) -> bool:
        """Say whether the person holds as many tokens as the project allows.

        Returns:
            True when knox's ``TOKEN_LIMIT_PER_USER`` is set and the person's
            working tokens have reached it.
        """
        limit = knox_settings.TOKEN_LIMIT_PER_USER
        return limit is not None and self.get_working_tokens().count() >= limit


class TokensView(TokenPageMixin, MVPTemplateView):
    """List the signed-in person's tokens."""

    template_name = "mvp_accounts/tokens/list.html"
    page_title = _("API tokens")
    page_subtitle = _(
        "A token lets a script or another tool use the API as you, "
        "without your password."
    )

    def get_breadcrumbs(self) -> list[dict]:
        """Lead back to the Account Center."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens")},
        ]

    def get_context_data(self, **kwargs):
        """Add the signed-in person's tokens and where they stand against the limit."""
        return super().get_context_data(
            tokens=self.get_working_tokens(),
            token_limit=knox_settings.TOKEN_LIMIT_PER_USER,
            at_limit=self.is_at_limit(),
            **kwargs,
        )


class CreateTokenView(TokenPageMixin, PageMixin, FormView):
    """Ask how long a new token should last, then create it through knox."""

    template_name = "mvp_accounts/tokens/create.html"
    form_class = CreateTokenForm
    page_title = _("Create a token")

    def get_success_url(self) -> str:
        """Return to the tokens page, whatever the request asked for."""
        return reverse("account_api_tokens")

    def form_valid(self, form: CreateTokenForm) -> HttpResponse:
        """Create the person's token with the chosen lifetime."""
        get_token_model().objects.create(
            user=self.request.user, expiry=form.get_expiry()
        )
        return super().form_valid(form)

    def get_breadcrumbs(self) -> list[dict]:
        """Lead back to the tokens page."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens"), "href": reverse("account_api_tokens")},
            {"text": _("Create")},
        ]


class RevokeTokenView(TokenPageMixin, MVPTemplateView):
    """Show the page that asks before one token is revoked."""

    template_name = "mvp_accounts/tokens/revoke.html"
    page_title = _("Revoke this token?")

    def get_breadcrumbs(self) -> list[dict]:
        """Lead back to the tokens page."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens"), "href": reverse("account_api_tokens")},
            {"text": _("Revoke")},
        ]

    def get_token(self):
        """Return the newest of the person's tokens that the address names.

        Raises:
            Http404: When the person holds no such token.
        """
        token = self.get_working_tokens().filter(token_key=self.kwargs["token_key"])
        if (found := token.first()) is None:
            raise Http404
        return found

    def get_context_data(self, **kwargs):
        """Add the token being revoked."""
        return super().get_context_data(token=self.get_token(), **kwargs)
