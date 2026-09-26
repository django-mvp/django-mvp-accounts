"""allauth's two-factor management pages render inside django-mvp's shell.

Every page is a management page: it carries the shell's stylesheet and the
sidebar's navigation, none of allauth's bare menu, and the form or text the page
exists for. Codes are real ones computed from the secret, since the suite never
accepts a fixed code.

The subject is a set of templates, not one source file, so this module does not
mirror a source file.
"""

import pytest
from django.core.cache import cache
from django.urls import reverse

from tests.factories import AuthenticatorFactory, EmailAddressFactory
from tests.test_management_pages import ManagementPageAssertions


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
