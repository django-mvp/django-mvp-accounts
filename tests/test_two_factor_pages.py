"""allauth's two-factor management pages render inside django-mvp's shell.

Every page is a management page: it carries the shell's stylesheet and the
sidebar's navigation, none of allauth's bare menu, and the form or text the page
exists for. Codes are real ones computed from the secret, since the suite never
accepts a fixed code.

The subject is a set of templates, not one source file, so this module does not
mirror a source file.
"""

import base64
import re

import pytest
from allauth.mfa.models import Authenticator
from bs4 import BeautifulSoup
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.urls import reverse

from tests.factories import AuthenticatorFactory, EmailAddressFactory
from tests.test_management_pages import ManagementPageAssertions, sidebar_menus


@pytest.fixture(autouse=True)
def fresh_caches():
    """Forget used codes and rate limits, which live in a cache that outlives a test."""
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


class TestTwoFactorOverview(ManagementPageAssertions):
    def test_with_nothing_set_up_it_offers_to_activate_and_to_add(
        self, fresh_client
    ) -> None:
        response = fresh_client.get(reverse("mfa_index"))

        html = self.assert_management_page(response, "Authenticator App")
        assert f'href="{reverse("mfa_activate_totp")}"' in html
        assert "Activate" in html
        assert f'href="{reverse("mfa_add_webauthn")}"' in html
        assert "Security Keys" in html
        assert "No security keys have been added." in html

    def test_it_is_not_allauths_bare_section(self, fresh_client) -> None:
        html = fresh_client.get(reverse("mfa_index")).content.decode()

        assert "<section" not in html

    def test_with_an_authenticator_app_it_offers_to_deactivate(
        self, fresh_client
    ) -> None:
        AuthenticatorFactory(user=fresh_client.user)
        AuthenticatorFactory(user=fresh_client.user, recovery_codes=True)

        html = self.assert_management_page(
            fresh_client.get(reverse("mfa_index")), "Recovery Codes"
        )

        assert f'href="{reverse("mfa_deactivate_totp")}"' in html
        assert f'href="{reverse("mfa_activate_totp")}"' not in html
        assert "Authentication using an authenticator app is active." in html

    def test_recovery_codes_report_their_count_and_offer_every_action(
        self, fresh_client
    ) -> None:
        AuthenticatorFactory(user=fresh_client.user)
        recovery = AuthenticatorFactory(user=fresh_client.user, recovery_codes=True)
        total = len(recovery.wrap().get_unused_codes())

        html = fresh_client.get(reverse("mfa_index")).content.decode()

        assert f"There are {total} out of {total} recovery codes available." in html
        for name in (
            "mfa_view_recovery_codes",
            "mfa_download_recovery_codes",
            "mfa_generate_recovery_codes",
        ):
            assert f'href="{reverse(name)}"' in html

    def test_without_authenticator_app_support_nothing_offers_it(
        self, fresh_client, rebuild_urls
    ) -> None:
        with rebuild_urls(MFA_SUPPORTED_TYPES=["recovery_codes", "webauthn"]):
            response = fresh_client.get(reverse("mfa_index"))

        html = self.assert_management_page(response, "Security Keys")
        assert "Authenticator App" not in html
        assert "mfa/totp" not in html

    def test_a_signed_out_visitor_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(reverse("mfa_index"))

        assert response.status_code == 302
        assert reverse("account_login") in response["Location"]


class TestActivateAuthenticatorApp(ManagementPageAssertions):
    @pytest.fixture
    def page(self, fresh_client) -> BeautifulSoup:
        response = fresh_client.get(reverse("mfa_activate_totp"))
        self.assert_management_page(response, 'name="code"')
        return BeautifulSoup(response.content.decode(), "html.parser")

    def test_the_qr_code_sits_on_white(self, page) -> None:
        assert "bg-white" in page.select_one("img[src^='data:image/svg+xml']")["class"]

    def test_the_stylesheet_defines_white(self) -> None:
        """A class the packaged stylesheet does not emit does nothing."""
        with open(finders.find("css/django-mvp.css")) as stylesheet:
            assert ".bg-white{" in stylesheet.read()

    def test_the_qr_code_is_drawn_in_a_dark_colour(self, page) -> None:
        uri = page.select_one("img[src^='data:image/svg+xml']")["src"]
        svg = base64.b64decode(uri.split(",", 1)[1]).decode()

        fill = re.search(r'<path[^>]*fill="([^"]+)"', svg).group(1)

        assert fill.lower() in {"#000", "#000000", "black"}

    def test_the_secret_is_shown(self, page, fresh_client) -> None:
        secret = fresh_client.session["mfa.totp.secret"]

        field = page.find(id="authenticator_secret")

        assert field.has_attr("disabled")
        assert field["value"] == secret

    def test_a_wrong_code_shows_allauths_error(self, fresh_client) -> None:
        fresh_client.get(reverse("mfa_activate_totp"))

        response = fresh_client.post(reverse("mfa_activate_totp"), {"code": "000000"})

        html = self.assert_management_page(response, 'name="code"')
        assert "Incorrect code." in html
        assert not Authenticator.objects.filter(user=fresh_client.user).exists()

    # allauth adds its message when the transaction commits. Inside the test's
    # own transaction that never happens, so this test commits for real.
    @pytest.mark.django_db(transaction=True)
    def test_a_correct_code_activates_and_says_so(
        self, fresh_client, totp_code
    ) -> None:
        fresh_client.get(reverse("mfa_activate_totp"))
        secret = fresh_client.session["mfa.totp.secret"]

        response = fresh_client.post(
            reverse("mfa_activate_totp"), {"code": totp_code(secret)}, follow=True
        )

        assert Authenticator.objects.filter(
            user=fresh_client.user, type=Authenticator.Type.TOTP
        ).exists()
        html = response.content.decode()
        assert "Authenticator app activated." in html
        assert sidebar_menus(html)


class TestDeactivateAuthenticatorApp(ManagementPageAssertions):
    @pytest.fixture
    def with_app(self, fresh_client):
        AuthenticatorFactory(user=fresh_client.user)
        return fresh_client

    def test_it_is_a_management_page(self, with_app) -> None:
        response = with_app.get(reverse("mfa_deactivate_totp"))

        html = self.assert_management_page(response, "Deactivate Authenticator App")
        assert "Are you sure?" in html

    def test_deactivating_says_so_and_leaves_nothing_active(self, with_app) -> None:
        response = with_app.post(reverse("mfa_deactivate_totp"), follow=True)

        html = response.content.decode()
        assert "Authenticator app deactivated." in html
        assert "An authenticator app is not active." in html
        assert not Authenticator.objects.filter(user=with_app.user).exists()


class TestRecoveryCodes(ManagementPageAssertions):
    @pytest.fixture
    def with_codes(self, fresh_client):
        AuthenticatorFactory(user=fresh_client.user)
        fresh_client.codes = (
            AuthenticatorFactory(user=fresh_client.user, recovery_codes=True)
            .wrap()
            .get_unused_codes()
        )
        return fresh_client

    def test_the_view_page_lists_every_unused_code_in_a_readonly_text_area(
        self, with_codes
    ) -> None:
        response = with_codes.get(reverse("mfa_view_recovery_codes"))

        html = self.assert_management_page(response, "Unused codes")
        area = BeautifulSoup(html, "html.parser").find("textarea", id="recovery_codes")
        assert area.has_attr("readonly")
        assert area.get_text().split() == with_codes.codes

    def test_the_view_page_hooks_resolve_when_codes_are_shown_once(
        self, with_codes, settings, assert_script_hooks
    ) -> None:
        settings.MFA_RECOVERY_CODES_SHOW_ONCE = True

        html = with_codes.get(reverse("mfa_view_recovery_codes")).content.decode()

        assert 'id="codes_saved"' in html
        assert assert_script_hooks(html) == 1

    def test_the_download_is_allauths_text_file_of_the_codes(self, with_codes) -> None:
        response = with_codes.get(reverse("mfa_download_recovery_codes"))

        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/plain")
        body = response.content.decode()
        for code in with_codes.codes:
            assert code in body

    def test_the_generate_page_is_a_management_page(self, with_codes) -> None:
        response = with_codes.get(reverse("mfa_generate_recovery_codes"))

        html = self.assert_management_page(response, "Generate")
        assert "This action will invalidate your existing codes." in html

    # allauth adds its message when the transaction commits, which never happens
    # inside the test's own transaction, so this test commits for real.
    @pytest.mark.django_db(transaction=True)
    def test_generating_replaces_the_codes_and_says_so(self, with_codes) -> None:
        response = with_codes.post(reverse("mfa_generate_recovery_codes"), follow=True)

        html = response.content.decode()
        assert "A new set of recovery codes has been generated." in html
        area = BeautifulSoup(html, "html.parser").find("textarea", id="recovery_codes")
        new_codes = area.get_text().split()
        assert new_codes
        assert set(new_codes).isdisjoint(with_codes.codes)
