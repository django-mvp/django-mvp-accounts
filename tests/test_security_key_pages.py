"""allauth's security-key and passkey pages render inside django-mvp's shell.

Signed-in pages are management pages, the sign-in and sign-up pages are entrance
pages. allauth's JavaScript drives every one of them, so each page also passes
the script-hook check: every element id the page's script names is on the page.
Passkey sign-up is off in the demo, so its pages are reached under settings
overrides.

The subject is a set of templates, not one source file, so this module does not
mirror a source file.
"""

import re

import pytest
from allauth.mfa.models import Authenticator
from bs4 import BeautifulSoup
from django.core import mail
from django.core.cache import cache
from django.urls import reverse

from tests.factories import AuthenticatorFactory, EmailAddressFactory
from tests.test_entrance_pages import EntrancePageAssertions
from tests.test_management_pages import ManagementPageAssertions


@pytest.fixture(autouse=True)
def fresh_caches():
    """Forget rate limits, which live in a cache that outlives a test."""
    cache.clear()


@pytest.fixture
def fresh_client(client, db):
    """A client that signed in through the form, so allauth need not ask again."""
    address = EmailAddressFactory()
    response = client.post(
        reverse("account_login"), {"login": address.email, "password": "password"}
    )
    assert response.status_code == 302
    client.user = address.user
    return client


@pytest.fixture
def two_keys(fresh_client):
    """A passkey named Laptop and a security key named Office."""
    user = fresh_client.user
    return (
        AuthenticatorFactory(user=user, webauthn=True, key_name="Laptop", passkey=True),
        AuthenticatorFactory(
            user=user, webauthn=True, key_name="Office", passkey=False
        ),
    )


class TestSecurityKeyList(ManagementPageAssertions):
    def test_it_lists_both_keys_with_edit_and_remove_links(
        self, fresh_client, two_keys
    ) -> None:
        response = fresh_client.get(reverse("mfa_list_webauthn"))

        html = self.assert_management_page(response, "Security Keys")
        soup = BeautifulSoup(html, "html.parser")
        assert "Laptop" in html
        assert "Office" in html
        for key in two_keys:
            assert soup.find("a", href=reverse("mfa_edit_webauthn", args=[key.pk]))
            assert soup.find("a", href=reverse("mfa_remove_webauthn", args=[key.pk]))

    def test_each_key_is_badged_as_a_passkey_or_a_security_key(
        self, fresh_client, two_keys
    ) -> None:
        response = fresh_client.get(reverse("mfa_list_webauthn"))

        rows = BeautifulSoup(response.content.decode(), "html.parser").select(
            "tbody tr"
        )
        by_name = {("Laptop" if "Laptop" in r.text else "Office"): r.text for r in rows}
        assert "Passkey" in by_name["Laptop"]
        assert "Security key" in by_name["Office"]

    def test_with_no_keys_it_says_so(self, fresh_client) -> None:
        response = fresh_client.get(reverse("mfa_list_webauthn"))

        html = self.assert_management_page(response, "Security Keys")
        assert "No security keys have been added." in html


class TestRenameSecurityKey(ManagementPageAssertions):
    def test_the_page_offers_the_name_form(self, fresh_client, two_keys) -> None:
        response = fresh_client.get(reverse("mfa_edit_webauthn", args=[two_keys[0].pk]))

        html = self.assert_management_page(response, 'name="name"')
        assert 'value="Laptop"' in html

    def test_saving_renames_the_key(self, fresh_client, two_keys) -> None:
        url = reverse("mfa_edit_webauthn", args=[two_keys[0].pk])

        response = fresh_client.post(url, {"name": "Desk"}, follow=True)

        assert response.redirect_chain[-1][0] == reverse("mfa_list_webauthn")
        two_keys[0].refresh_from_db()
        assert two_keys[0].data["name"] == "Desk"
        assert "Desk" in response.content.decode()


class TestRemoveSecurityKey(ManagementPageAssertions):
    def test_the_page_asks_for_confirmation(self, fresh_client, two_keys) -> None:
        response = fresh_client.get(
            reverse("mfa_remove_webauthn", args=[two_keys[1].pk])
        )

        self.assert_management_page(response, "<form")

    def test_confirming_removes_the_key_and_shows_allauths_message(
        self, fresh_client, two_keys
    ) -> None:
        url = reverse("mfa_remove_webauthn", args=[two_keys[1].pk])

        response = fresh_client.post(url, follow=True)

        assert not Authenticator.objects.filter(pk=two_keys[1].pk).exists()
        assert "Security key removed." in response.content.decode()


class TestStoredKeysSurviveAuthentication(ManagementPageAssertions):
    def test_reauthentication_parses_a_stored_key(self, fresh_client, two_keys) -> None:
        response = fresh_client.get(reverse("mfa_reauthenticate_webauthn"))

        assert response.status_code == 200


class TestAddSecurityKey(ManagementPageAssertions):
    def test_the_page_carries_every_hook_the_script_looks_for(
        self, fresh_client, assert_script_hooks
    ) -> None:
        response = fresh_client.get(reverse("mfa_add_webauthn"))

        html = self.assert_management_page(response, 'id="mfa_webauthn_add"')
        assert assert_script_hooks(html) >= 1
        soup = BeautifulSoup(html, "html.parser")
        assert soup.find(id="id_passwordless"), "the passkey checkbox is missing"
        assert soup.find(id="id_credential"), "the credential input is missing"
        assert soup.find("input", attrs={"name": "name"})

    def test_a_missing_hook_is_caught(self, fresh_client, assert_script_hooks) -> None:
        html = fresh_client.get(reverse("mfa_add_webauthn")).content.decode()

        with pytest.raises(AssertionError, match="mfa_webauthn_add"):
            assert_script_hooks(html.replace('id="mfa_webauthn_add"', ""))


class TestPasskeySignIn(EntrancePageAssertions):
    def test_the_sign_in_page_offers_a_passkey(
        self, client, db, assert_script_hooks
    ) -> None:
        response = client.get(reverse("account_login"))

        html = self.assert_entrance_page(response, 'name="login"')
        soup = BeautifulSoup(html, "html.parser")
        button = soup.find(id="passkey_login")
        assert button is not None, "the passkey button is missing"
        assert button["form"] == "mfa_login"
        assert "Sign in with a passkey" in button.get_text()
        form = soup.find("form", id="mfa_login")
        assert form.find("input", id="mfa_credential")
        assert form["action"] == reverse("mfa_login_webauthn")
        assert assert_script_hooks(html) >= 1

    def test_with_passkey_sign_in_off_the_page_offers_none(
        self, client, db, rebuild_urls
    ) -> None:
        with rebuild_urls(MFA_PASSKEY_LOGIN_ENABLED=False):
            response = client.get(reverse("account_login"))

        html = self.assert_entrance_page(response, 'name="login"')
        assert 'id="passkey_login"' not in html
        assert 'id="mfa_login"' not in html
        assert 'id="mfa_credential"' not in html
        assert "allauth.webauthn.forms.loginForm" not in html


VERIFICATION_CODE = re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}$", re.MULTILINE)
PASSKEY_SIGNUP = {
    "MFA_PASSKEY_SIGNUP_ENABLED": True,
    "ACCOUNT_EMAIL_VERIFICATION": "mandatory",
    "ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED": True,
}


class TestPasskeySignUp(EntrancePageAssertions):
    """The demo leaves passkey sign-up off, so these run under settings overrides."""

    def test_the_passkey_sign_up_page_is_an_entrance_page(
        self, client, db, rebuild_urls
    ) -> None:
        with rebuild_urls(**PASSKEY_SIGNUP):
            response = client.get(reverse("account_signup_by_passkey"))

        self.assert_entrance_page(response, 'name="email"')

    def test_after_the_email_code_the_person_creates_the_passkey(
        self, client, db, rebuild_urls, assert_script_hooks
    ) -> None:
        with rebuild_urls(**PASSKEY_SIGNUP):
            client.post(
                reverse("account_signup_by_passkey"), {"email": "passkey@example.com"}
            )
            code = VERIFICATION_CODE.search(mail.outbox[-1].body).group(0)
            response = client.post(
                reverse("account_email_verification_sent"), {"code": code}, follow=True
            )
            passkey_page = reverse("mfa_signup_webauthn")

        assert response.redirect_chain[-1][0] == passkey_page
        html = self.assert_entrance_page(response, 'id="mfa_webauthn_signup"')
        assert assert_script_hooks(html) >= 1


class TestReauthenticateWithSecurityKey(ManagementPageAssertions):
    def test_it_is_a_management_page_with_the_hooks_the_script_needs(
        self, client, db, assert_script_hooks
    ) -> None:
        address = EmailAddressFactory()
        AuthenticatorFactory(user=address.user, webauthn=True, key_name="Office")
        client.force_login(address.user)

        response = client.get(reverse("mfa_reauthenticate_webauthn"))

        html = self.assert_management_page(response, 'id="mfa_webauthn_reauthenticate"')
        assert assert_script_hooks(html) >= 1


class TestSecurityKeysTurnedOff(ManagementPageAssertions):
    """A project that leaves ``webauthn`` out of MFA_SUPPORTED_TYPES offers no key."""

    TYPES = ["totp", "recovery_codes"]

    def test_the_overview_names_no_security_key_and_links_to_no_key_page(
        self, fresh_client, rebuild_urls
    ) -> None:
        key_pages = reverse("mfa_list_webauthn")
        with rebuild_urls(MFA_SUPPORTED_TYPES=self.TYPES):
            response = fresh_client.get(reverse("mfa_index"))

        html = self.assert_management_page(response, "Authenticator App")
        assert "Security Key" not in html
        assert "Passkey" not in html
        assert key_pages not in html

    def test_the_second_factor_step_offers_no_security_key(
        self, client, db, rebuild_urls
    ) -> None:
        address = EmailAddressFactory()
        AuthenticatorFactory(user=address.user)
        AuthenticatorFactory(user=address.user, webauthn=True)

        with rebuild_urls(MFA_SUPPORTED_TYPES=self.TYPES):
            client.post(
                reverse("account_login"),
                {"login": address.email, "password": "password"},
            )
            response = client.get(reverse("mfa_authenticate"))

        html = response.content.decode()
        assert response.status_code == 200
        assert 'name="code"' in html
        assert "webauthn_form" not in html
        assert "mfa_webauthn_authenticate" not in html
