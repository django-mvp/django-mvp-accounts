"""Every email allauth sends has an HTML part on django-mvp's email layout.

allauth renders ``<prefix>_message.html`` when it exists and sends it beside
its own plain text. Each email is rendered the way allauth renders it, through
the account adapter, and asserted on the HTML part: that there is one, that it
is built on the layout, and that it carries the link, code or data the person
needs. The plain-text part stays allauth's own.
"""

import pytest
from allauth.account.adapter import get_adapter
from allauth.core.context import request_context
from django.contrib.sites.shortcuts import get_current_site
from django.test import RequestFactory

from tests.factories import EmailAddressFactory

# The table every email on django-mvp's layout is drawn in.
LAYOUT = 'class="mvp-email-card'

LINK = "https://testserver/accounts/action/abc/"
CODE = "Q7KX-2M9P"

NOTIFICATION = {"ip": "203.0.113.9", "user_agent": "TestBrowser/1.0"}

# Each email allauth sends: the context it passes, and what the HTML part must
# carry for the person reading it.
EMAILS = {
    "account/email/email_confirmation": ({"activate_url": LINK}, [f'href="{LINK}"']),
    "account/email/email_confirmation_signup": (
        {"activate_url": LINK},
        [f'href="{LINK}"'],
    ),
    "account/email/login_code": ({"code": CODE}, [CODE]),
    "account/email/password_reset_code": ({"code": CODE}, [CODE]),
    "account/email/password_reset_key": (
        {"password_reset_url": LINK, "username": "ada"},
        [f'href="{LINK}"', "ada"],
    ),
    "account/email/account_already_exists": (
        {"password_reset_url": LINK, "signup_url": "https://testserver/signup/"},
        [f'href="{LINK}"', "person@example.com"],
    ),
    "account/email/unknown_account": (
        {"signup_url": LINK},
        [f'href="{LINK}"', "person@example.com"],
    ),
    "account/email/email_changed": (
        {**NOTIFICATION, "from_email": "old@example.com", "to_email": "new@example.com"},
        ["old@example.com", "new@example.com"],
    ),
    "account/email/email_deleted": (
        {**NOTIFICATION, "deleted_email": "gone@example.com"},
        ["gone@example.com"],
    ),
    "account/email/password_changed": (NOTIFICATION, []),
    "account/email/password_reset": (NOTIFICATION, []),
    "account/email/password_set": (NOTIFICATION, []),
    "mfa/email/recovery_codes_generated": (NOTIFICATION, []),
    "mfa/email/totp_activated": (NOTIFICATION, []),
    "mfa/email/totp_deactivated": (NOTIFICATION, []),
    "mfa/email/webauthn_added": (NOTIFICATION, []),
    "mfa/email/webauthn_removed": (NOTIFICATION, []),
    "socialaccount/email/account_connected": (
        {**NOTIFICATION, "provider": "GitHub"},
        ["GitHub"],
    ),
    "socialaccount/email/account_disconnected": (
        {**NOTIFICATION, "provider": "GitHub"},
        ["GitHub"],
    ),
}

CARRYING = [prefix for prefix, (_, carried) in EMAILS.items() if carried]
NOTIFICATIONS = [prefix for prefix, (context, _) in EMAILS.items() if "ip" in context]


@pytest.fixture
def render_mail(db):
    """Render an email as allauth's adapter does, inside a request."""
    address = EmailAddressFactory(email="person@example.com")

    def render(prefix: str, context: dict):
        request = RequestFactory().get("/", secure=True)
        request.user = address.user
        with request_context(request):
            adapter = get_adapter(request)
            message = adapter.render_mail(
                prefix,
                address.email,
                {
                    "request": request,
                    "email": address.email,
                    "user": address.user,
                    "current_site": get_current_site(request),
                    **context,
                },
            )
        html = [body for body, kind in message.alternatives if kind == "text/html"]
        return message, (html[0] if html else None)

    return render


class TestAllauthEmails:
    @pytest.mark.parametrize("prefix", EMAILS)
    def test_has_an_html_part_on_the_layout(self, render_mail, prefix) -> None:
        context, _ = EMAILS[prefix]

        message, html = render_mail(prefix, context)

        assert html is not None
        assert LAYOUT in html
        assert "<html" not in message.body

    @pytest.mark.parametrize("prefix", CARRYING)
    def test_html_part_carries_what_the_email_is_for(self, render_mail, prefix) -> None:
        context, carried = EMAILS[prefix]

        _, html = render_mail(prefix, context)

        for value in carried:
            assert value in html

    def test_confirmation_by_code_carries_the_code_and_no_link(
        self, render_mail
    ) -> None:
        _, html = render_mail("account/email/email_confirmation", {"code": CODE})

        assert CODE in html
        assert "/accounts/" not in html

    @pytest.mark.parametrize("prefix", NOTIFICATIONS)
    def test_notification_says_where_the_change_came_from(
        self, render_mail, prefix
    ) -> None:
        context, _ = EMAILS[prefix]

        _, html = render_mail(prefix, context)

        assert "203.0.113.9" in html
        assert "TestBrowser/1.0" in html

    def test_notification_without_an_address_shows_a_dash(self, render_mail) -> None:
        _, html = render_mail(
            "account/email/password_changed", {"ip": None, "user_agent": ""}
        )

        assert html.count("—") >= 2

    def test_html_part_escapes_what_it_is_given(self, render_mail) -> None:
        _, html = render_mail(
            "socialaccount/email/account_connected",
            {**NOTIFICATION, "provider": "<script>x</script>"},
        )

        assert "<script>x</script>" not in html
        assert "&lt;script&gt;" in html
