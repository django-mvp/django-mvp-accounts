"""The API tokens pages: a person's list, a create form and a revoke confirmation.

Only a project that routes ``mvp_accounts.tokens.urls`` ever imports this module,
which is why it may import django-rest-knox where nothing else in the package may.
"""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import FormView
from knox.models import get_token_model
from knox.settings import CONSTANTS, knox_settings
from mvp.views import MVPTemplateView
from mvp.views.base import PageMixin

from mvp_accounts.tokens.forms import CreateTokenForm

SHOWN_ONCE_COOKIE = "mvp_accounts_new_token"
SHOWN_ONCE_SALT = "mvp_accounts.tokens.new_token"
SHOWN_ONCE_MAX_AGE = 60


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


@method_decorator(never_cache, name="dispatch")
class TokensView(TokenPageMixin, MVPTemplateView):
    """List the signed-in person's tokens, and show a new one the one time."""

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

    def get_new_token(self) -> dict[str, str] | None:
        """Return the token just created, if the cookie names one of the person's.

        Returns:
            The complete ``value`` and its ``token_key``, or ``None`` when the
            cookie is missing, tampered with, too old, or holds a token that is
            not one of the signed-in person's working tokens.
        """
        value = self.request.get_signed_cookie(
            SHOWN_ONCE_COOKIE,
            default=None,
            salt=SHOWN_ONCE_SALT,
            max_age=SHOWN_ONCE_MAX_AGE,
        )
        if value is None:
            return None
        token_key = value[: CONSTANTS.TOKEN_KEY_LENGTH]
        if not self.get_working_tokens().filter(token_key=token_key).exists():
            return None
        return {"value": value, "token_key": token_key}

    def get_context_data(self, **kwargs):
        """Add the person's tokens, the limit, and a token created a moment ago."""
        return super().get_context_data(
            tokens=self.get_working_tokens(),
            token_limit=knox_settings.TOKEN_LIMIT_PER_USER,
            at_limit=self.is_at_limit(),
            new_token=self.get_new_token(),
            header_prefix=knox_settings.AUTH_HEADER_PREFIX,
            **kwargs,
        )

    def get(self, request, *args, **kwargs):
        """Delete the new-token cookie on the response that reads it."""
        response = super().get(request, *args, **kwargs)
        response.delete_cookie(
            SHOWN_ONCE_COOKIE, path=reverse("account_api_tokens"), samesite="Strict"
        )
        return response


class CreateTokenView(TokenPageMixin, PageMixin, FormView):
    """Ask how long a new token should last, then create it through knox."""

    template_name = "mvp_accounts/tokens/create.html"
    form_class = CreateTokenForm
    page_title = _("Create a token")

    def get(self, request, *args, **kwargs):
        """Send a person who is at the limit back to the tokens page."""
        if self.is_at_limit():
            return self.refuse_at_limit()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Create nothing for a person who is at the limit."""
        if self.is_at_limit():
            return self.refuse_at_limit()
        return super().post(request, *args, **kwargs)

    def refuse_at_limit(self) -> HttpResponse:
        """Say the limit is reached and return to the tokens page.

        Returns:
            A redirect to the tokens page, with an error message added.
        """
        messages.error(
            self.request,
            _("You hold as many tokens as this site allows. Revoke one first."),
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """Return to the tokens page, whatever the request asked for."""
        return reverse("account_api_tokens")

    def form_valid(self, form: CreateTokenForm) -> HttpResponse:
        """Create the person's token and hand its value to the next page, once."""
        created = get_token_model().objects.create(
            user=self.request.user, expiry=form.get_expiry()
        )
        # knox returns the record and the complete value, which only it ever holds.
        value = created[1]
        response = super().form_valid(form)
        response.set_signed_cookie(
            SHOWN_ONCE_COOKIE,
            value,
            salt=SHOWN_ONCE_SALT,
            max_age=SHOWN_ONCE_MAX_AGE,
            path=self.get_success_url(),
            secure=self.request.is_secure(),
            httponly=True,
            samesite="Strict",
        )
        return response

    def get_breadcrumbs(self) -> list[dict]:
        """Lead back to the tokens page."""
        return [
            {"text": _("Account Center"), "href": reverse("account-center")},
            {"text": _("API tokens"), "href": reverse("account_api_tokens")},
            {"text": _("Create")},
        ]


class RevokeTokenView(TokenPageMixin, MVPTemplateView):
    """Ask before one token is revoked, then revoke it."""

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

        Returns:
            The token record, or ``None`` when the address names a key that is
            unknown, expired or another person's.
        """
        return (
            self.get_working_tokens().filter(token_key=self.kwargs["token_key"]).first()
        )

    def refuse_gone(self) -> HttpResponse:
        """Say the token no longer exists and return to the tokens page.

        A key that is unknown, expired or another person's all end here, so the
        response never tells them apart.

        Returns:
            A redirect to the tokens page, with a warning message added.
        """
        messages.warning(self.request, _("That token no longer exists."))
        return HttpResponseRedirect(reverse("account_api_tokens"))

    def get(self, request, *args, **kwargs):
        """Show the token being revoked, and delete nothing."""
        self.token = self.get_token()
        if self.token is None:
            return self.refuse_gone()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Revoke the one token the address names, or leave a gone one alone."""
        token = self.get_token()
        if token is None:
            return self.refuse_gone()
        token.delete()
        messages.success(request, _("The token has been revoked."))
        return HttpResponseRedirect(reverse("account_api_tokens"))

    def get_context_data(self, **kwargs):
        """Add the token being revoked."""
        return super().get_context_data(token=self.token, **kwargs)
