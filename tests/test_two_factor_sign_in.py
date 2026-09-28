"""The second-factor step of signing in renders inside django-mvp's shell.

The step and the "trust this browser" prompt are entrance pages: the shell's
stylesheet, no navigation, none of allauth's bare menu. Re-authentication with a
code is a management page, since the person is already signed in. Codes are real
ones computed from the secret, since the suite never accepts a fixed code.

The subject is a set of templates, not one source file, so this module does not
mirror a source file.
"""

import pytest
from allauth.mfa.models import Authenticator
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.urls import reverse

from tests.factories import AuthenticatorFactory, EmailAddressFactory
from tests.test_entrance_pages import EntrancePageAssertions
from tests.test_management_pages import ManagementPageAssertions


@pytest.fixture(autouse=True)
def fresh_caches():
    cache.clear()


@pytest.fixture
def two_factor_user(db):
    address = EmailAddressFactory()
    user = address.user
    user.email_address = address.email
    app = AuthenticatorFactory(user=user)
    AuthenticatorFactory(user=user, recovery_codes=True)
    user.secret = app.data["secret"]
    return user


def sign_in(client, user):
    """Post the password form, which is where the second-factor step begins."""
    return client.post(
        reverse("account_login"),
        {"login": user.email_address, "password": "password"},
    )


class TestSecondFactorStep(EntrancePageAssertions):
    @pytest.fixture(autouse=True)
    def no_trust_prompt(self, settings) -> None:
        settings.MFA_TRUST_ENABLED = False

    def test_the_password_leads_to_the_step(self, client, two_factor_user) -> None:
        response = sign_in(client, two_factor_user)

        assert response.status_code == 302
        assert response["Location"] == reverse("mfa_authenticate")

    def test_the_step_is_an_entrance_page_with_the_code_form(
        self, client, two_factor_user
    ) -> None:
        sign_in(client, two_factor_user)

        response = client.get(reverse("mfa_authenticate"))

        self.assert_entrance_page(response, 'name="code"')

    def test_a_correct_code_finishes_signing_in(
        self, client, two_factor_user, totp_code
    ) -> None:
        sign_in(client, two_factor_user)

        response = client.post(
            reverse("mfa_authenticate"), {"code": totp_code(two_factor_user.secret)}
        )

        assert response.status_code == 302
        overview = client.get(reverse("overview"))
        assert overview.wsgi_request.user == two_factor_user

    def test_an_unused_recovery_code_finishes_signing_in(
        self, client, two_factor_user
    ) -> None:
        recovery = Authenticator.objects.get(
            user=two_factor_user, type=Authenticator.Type.RECOVERY_CODES
        ).wrap()
        code = recovery.get_unused_codes()[0]
        sign_in(client, two_factor_user)

        response = client.post(reverse("mfa_authenticate"), {"code": code})

        assert response.status_code == 302
        overview = client.get(reverse("overview"))
        assert overview.wsgi_request.user == two_factor_user

    def test_a_wrong_code_is_rejected(self, client, two_factor_user) -> None:
        sign_in(client, two_factor_user)

        response = client.post(reverse("mfa_authenticate"), {"code": "000000"})

        self.assert_entrance_page(response, 'name="code"')
        assert "code" in response.context["form"].errors
        overview = client.get(reverse("overview"))
        assert not overview.wsgi_request.user.is_authenticated

    def test_the_security_key_form_keeps_the_id_allauths_script_binds(
        self, client, two_factor_user, assert_script_hooks
    ) -> None:
        sign_in(client, two_factor_user)

        response = client.get(reverse("mfa_authenticate"))

        html = response.content.decode()
        page = BeautifulSoup(html, "html.parser")
        assert page.find("form", id="webauthn_form")
        assert page.find(id="mfa_webauthn_authenticate")
        assert assert_script_hooks(html) >= 1

    def test_without_security_key_support_the_page_has_no_such_form(
        self, client, two_factor_user, rebuild_urls
    ) -> None:
        with rebuild_urls(MFA_SUPPORTED_TYPES=["totp", "recovery_codes"]):
            sign_in(client, two_factor_user)
            response = client.get(reverse("mfa_authenticate"))

        html = self.assert_entrance_page(response, 'name="code"')
        assert "webauthn_form" not in html


class TestActivateThenSignIn(EntrancePageAssertions):
    @pytest.mark.django_db(transaction=True)
    def test_a_code_then_a_recovery_code_each_finish_signing_in(
        self, client, settings, totp_code
    ) -> None:
        settings.MFA_TRUST_ENABLED = False
        address = EmailAddressFactory()
        client.post(
            reverse("account_login"),
            {"login": address.email, "password": "password"},
        )
        client.get(reverse("mfa_activate_totp"))
        secret = client.session["mfa.totp.secret"]
        client.post(reverse("mfa_activate_totp"), {"code": totp_code(secret)})
        recovery = Authenticator.objects.get(
            user=address.user, type=Authenticator.Type.RECOVERY_CODES
        ).wrap()
        codes = recovery.get_unused_codes()
        client.post(reverse("account_logout"))

        # A code is refused twice in its period, so the sign-in that follows the
        # activation uses a recovery code and the one after it uses the app.
        response = client.post(
            reverse("account_login"),
            {"login": address.email, "password": "password"},
        )
        assert response["Location"] == reverse("mfa_authenticate")
        self.assert_entrance_page(
            client.get(reverse("mfa_authenticate")), 'name="code"'
        )
        client.post(reverse("mfa_authenticate"), {"code": codes[0]})
        assert client.get(reverse("overview")).wsgi_request.user == address.user
        client.post(reverse("account_logout"))

        cache.clear()
        client.post(
            reverse("account_login"),
            {"login": address.email, "password": "password"},
        )
        client.post(reverse("mfa_authenticate"), {"code": totp_code(secret)})
        assert client.get(reverse("overview")).wsgi_request.user == address.user


class TestTrustThisBrowser(EntrancePageAssertions):
    @pytest.fixture
    def at_trust_prompt(self, client, two_factor_user, rebuild_urls, totp_code):
        # The prompt's route exists only when the setting is on as allauth's
        # URLconf is imported.
        with rebuild_urls(MFA_TRUST_ENABLED=True):
            sign_in(client, two_factor_user)
            response = client.post(
                reverse("mfa_authenticate"),
                {"code": totp_code(two_factor_user.secret)},
            )
            assert response["Location"] == reverse("mfa_trust")
            yield client

    def test_passing_the_step_leads_to_the_prompt(self, at_trust_prompt) -> None:
        response = at_trust_prompt.get(reverse("mfa_trust"))

        html = self.assert_entrance_page(response, 'value="trust"')
        assert 'value="skip"' in html

    @pytest.mark.parametrize("choice", ["trust", "skip"])
    def test_either_choice_finishes_signing_in(
        self, at_trust_prompt, two_factor_user, choice
    ) -> None:
        response = at_trust_prompt.post(reverse("mfa_trust"), {"action": choice})

        assert response.status_code == 302
        overview = at_trust_prompt.get(reverse("overview"))
        assert overview.wsgi_request.user == two_factor_user


class TestReauthenticateWithACode(ManagementPageAssertions):
    @pytest.fixture
    def stale_client(self, client, two_factor_user):
        client.force_login(two_factor_user)
        return client

    @pytest.fixture
    def code_page_url(self) -> str:
        return f"{reverse('mfa_reauthenticate')}?next={reverse('mfa_deactivate_totp')}"

    def test_the_password_page_offers_a_code_instead(self, stale_client) -> None:
        response = stale_client.get(reverse("mfa_deactivate_totp"), follow=True)

        assert reverse("mfa_reauthenticate") in response.content.decode()

    def test_the_code_page_is_a_management_page(
        self, stale_client, code_page_url
    ) -> None:
        response = stale_client.get(code_page_url)

        self.assert_management_page(response, 'name="code"')

    def test_a_wrong_code_is_rejected(self, stale_client, code_page_url) -> None:
        response = stale_client.post(code_page_url, {"code": "000000"})

        self.assert_management_page(response, 'name="code"')
        assert "code" in response.context["form"].errors

    def test_a_correct_code_continues_to_the_page_asked_for(
        self, stale_client, two_factor_user, totp_code, code_page_url
    ) -> None:
        response = stale_client.post(
            code_page_url,
            {
                "code": totp_code(two_factor_user.secret),
                "next": reverse("mfa_deactivate_totp"),
            },
            follow=True,
        )

        assert response.redirect_chain[-1][0] == reverse("mfa_deactivate_totp")
        self.assert_management_page(
            response, f'action="{reverse("mfa_deactivate_totp")}"'
        )
