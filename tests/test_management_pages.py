"""allauth's account management pages render inside django-mvp's shell.

A page that falls back to allauth's bare markup still answers 200 and still
shows its form, so the status code proves nothing. Every page is asserted on
what it renders: the shell's stylesheet, the sidebar's navigation menu, none of
allauth's own menu, and the form the page exists for.

The subject is a pair of templates, ``allauth/layouts/manage.html`` and
``account/base_entrance.html``, so this module does not mirror a source file.
"""

import re

import pytest
from allauth.account.models import EmailAddress
from django.core.cache import cache
from django.urls import reverse

from tests.factories import EmailAddressFactory, PhoneNumberFactory, UserFactory

STYLESHEET = "css/django-mvp.css"
NAVIGATION = 'aria-label="Main navigation"'
ALLAUTH_BARE_MENU = "<strong>Menu:</strong>"
SIDEBAR_MENU = re.compile(r'<ul[^>]*role="navigation"[^>]*aria-label="([^"]+)"')
SMS_CODE = re.compile(r"your verification code is ([\w-]+)")
NEW_PHONE = "+491510000123"


def sidebar_menus(html: str) -> list[str]:
    """The labels of the navigation menus the page draws."""
    return SIDEBAR_MENU.findall(html)


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Forget allauth's rate limits, which live in a cache that outlives a test."""
    cache.clear()


@pytest.fixture
def fresh_client(client, db):
    """A client that signed in through the sign-in form.

    allauth asks for the password again before a sensitive change unless the
    session records a recent sign-in, and ``force_login`` records none.
    """
    address = EmailAddressFactory()
    response = client.post(
        reverse("account_login"), {"login": address.email, "password": "password"}
    )
    assert response.status_code == 302
    client.user = address.user
    return client


class ManagementPageAssertions:
    """The four things every management page is asserted to be."""

    def assert_management_page(self, response, form_marker: str) -> str:
        html = response.content.decode()

        assert response.status_code == 200
        assert STYLESHEET in html, "the shell's stylesheet is not on the page"
        assert sidebar_menus(html), "the sidebar draws no navigation menu"
        assert ALLAUTH_BARE_MENU not in html, "allauth's bare layout rendered"
        assert form_marker in html, "the page's own form is missing"
        return html


class TestManagementPages(ManagementPageAssertions):
    def test_email_page_lists_every_address(self, signed_in_client) -> None:
        user = signed_in_client.user
        EmailAddressFactory(user=user, email="second@example.com", primary=False)
        EmailAddressFactory(
            user=user, email="third@example.com", primary=False, verified=False
        )

        response = signed_in_client.get(reverse("account_email"))

        html = self.assert_management_page(response, 'name="action_primary"')
        for address in EmailAddress.objects.filter(user=user):
            assert address.email in html
        assert html.count("Verified") >= 2
        assert "Unverified" in html
        assert "Primary" in html
        for action in ("action_send", "action_remove", "action_add"):
            assert f'name="{action}"' in html

    def test_email_page_sidebar_draws_the_account_center_menu(
        self, signed_in_client
    ) -> None:
        response = signed_in_client.get(reverse("account_email"))

        html = response.content.decode()
        assert sidebar_menus(html)[0] == "Account navigation"
        assert NAVIGATION not in html

    def test_change_email(self, signed_in_client, rebuild_urls) -> None:
        with rebuild_urls(ACCOUNT_CHANGE_EMAIL=True):
            response = signed_in_client.get(reverse("account_email"))

        html = self.assert_management_page(response, 'name="action_add"')
        assert "Change Email" in html
        assert signed_in_client.user.email in html

    def test_password_change(self, signed_in_client) -> None:
        response = signed_in_client.get(reverse("account_change_password"))

        html = self.assert_management_page(response, 'name="oldpassword"')
        assert sidebar_menus(html)[0] == "Account navigation"

    def test_password_set_for_an_account_without_a_password(self, client, db) -> None:
        user = UserFactory(password=None)
        user.set_unusable_password()
        user.save()
        EmailAddressFactory(user=user)
        client.force_login(user)

        response = client.get(reverse("account_set_password"), follow=True)

        self.assert_management_page(response, 'name="password1"')

    def test_phone_change(self, signed_in_client) -> None:
        PhoneNumberFactory(user=signed_in_client.user)

        response = signed_in_client.get(reverse("account_change_phone"))

        html = self.assert_management_page(response, 'name="phone"')
        assert sidebar_menus(html)[0] == "Account navigation"

    def test_phone_verification_by_code_when_signed_in(
        self, fresh_client, capsys
    ) -> None:
        response = fresh_client.post(
            reverse("account_change_phone"), {"phone": NEW_PHONE}, follow=True
        )

        self.assert_management_page(response, 'name="code"')
        assert response.redirect_chain[-1][0] == reverse("account_verify_phone")
        code = SMS_CODE.search(capsys.readouterr().out).group(1)

        confirmed = fresh_client.post(
            reverse("account_verify_phone"), {"code": code}, follow=True
        )

        assert confirmed.redirect_chain[-1][0] == reverse("account_change_phone")
        html = confirmed.content.decode()
        assert "Incorrect code" not in html
        assert f"You have verified phone number {NEW_PHONE}" in html

    def test_reauthentication(self, signed_in_client) -> None:
        response = signed_in_client.get(reverse("account_reauthenticate"))

        html = self.assert_management_page(response, 'name="password"')
        assert "Confirm Access" in html

    def test_a_message_allauth_adds_shows_in_the_shell(self, signed_in_client) -> None:
        user = signed_in_client.user
        EmailAddressFactory(
            user=user, email="pending@example.com", primary=False, verified=False
        )

        response = signed_in_client.post(
            reverse("account_email"),
            {"email": "pending@example.com", "action_send": ""},
            follow=True,
        )

        html = response.content.decode()
        assert "Confirmation email sent to pending@example.com" in html
        assert html.index("Confirmation email sent") > html.index(STYLESHEET)
        assert 'role="alert"' in html
        assert sidebar_menus(html)

    @pytest.mark.skip(
        reason="django-mvp#358: allauth's content block replaces the Account "
        "Center layout's container"
    )
    def test_page_body_sits_inside_the_account_center_container(
        self, signed_in_client
    ) -> None:
        response = signed_in_client.get(reverse("account_email"))

        html = response.content.decode()
        assert html.index("container mx-auto") < html.index("Email Addresses")


class TestPhoneVerificationBase(ManagementPageAssertions):
    """The same code page is an entrance page during sign-up (FR-003)."""

    def test_verification_during_sign_up_is_an_entrance_page(
        self, client, db, capsys
    ) -> None:
        response = client.post(
            reverse("account_signup"),
            {
                "email": "newcomer@example.com",
                "password1": "a-long-Password-1",
                "password2": "a-long-Password-1",
                "phone": NEW_PHONE,
            },
            follow=True,
        )

        html = response.content.decode()
        assert response.redirect_chain[-1][0] == reverse("account_verify_phone")
        assert 'name="code"' in html
        assert STYLESHEET in html
        assert not sidebar_menus(html), "an entrance page draws no navigation"
        assert NAVIGATION not in html
        assert ALLAUTH_BARE_MENU not in html


class TestWarnNoEmail:
    """allauth's no-address warning shows inside the shell as an alert (US4)."""

    def test_the_warning_is_drawn_as_an_alert(self, client, db) -> None:
        user = UserFactory(email="")
        client.force_login(user)

        html = client.get(reverse("account_email")).content.decode()

        assert STYLESHEET in html
        assert "You currently do not have any email address set up" in html
        alert = re.search(
            r'<div role="alert"[^>]*class="alert alert-warning[^"]*"', html
        ) or re.search(r'class="alert alert-warning[^"]*"[^>]*role="alert"', html)
        assert alert, "the warning is not drawn as a warning alert"
        assert html.index("alert-warning") < html.index("You currently do not have")
