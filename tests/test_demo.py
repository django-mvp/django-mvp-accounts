"""The demo project renders.

Everything in the demo fails quietly. An unresolvable Cotton component renders
as empty output, a Tailwind class the packaged stylesheet does not emit does
nothing, and a menu entry whose URL will not resolve is dropped from the tree.
None of those raise, so the demo is asserted against its rendered pages rather
than against the objects that built them.
"""

from io import StringIO

import pytest
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount
from allauth.usersessions.models import UserSession
from django.contrib.sessions.models import Session
from django.core.mail import EmailMessage
from django.core.management import CommandError, call_command
from django.urls import NoReverseMatch, reverse

from demo import settings as demo_settings
from demo.adapter import DemoAccountAdapter
from demo.mail import OutboxEmailBackend
from tests.factories import PhoneNumberFactory, UserFactory


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        """The page is inside django-mvp's application shell, not bare.

        A template that fails to extend the shell still returns 200 and still
        shows its own content, so the status code proves nothing about this.
        """
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_holds_the_pages_that_exist(self, overview_page: str) -> None:
        """A menu entry naming a route that will not resolve is dropped.

        It is dropped silently, which is why the assertion is on the rendered
        sidebar rather than on the menu tree that produced it.
        """
        assert "Overview" in overview_page

    def test_the_starter_component_reached_the_page(self, overview_page: str) -> None:
        """Delete this test with the starter component.

        Cotton renders a component it cannot resolve as empty output, so this
        is the assertion that would catch a moved or renamed template.
        """
        assert "It renders" in overview_page


class TestDemoSignIn:
    """The demo runs allauth, so its sign-in is allauth's page and flow."""

    def test_allauths_sign_in_page_responds(self, client, db) -> None:
        assert client.get(reverse("account_login")).status_code == 200

    def test_a_seeded_account_signs_in_with_the_demo_password(
        self, client, db, settings
    ) -> None:
        settings.DEBUG = True
        call_command("seed_demo", stdout=StringIO())

        response = client.post(
            reverse("account_login"),
            {"login": "regular.user@example.com", "password": "password"},
        )

        assert response.status_code == 302
        overview = client.get(reverse("overview"))
        assert overview.wsgi_request.user.is_authenticated

    def test_seeding_twice_leaves_one_verified_primary_address_each(
        self, db, settings
    ) -> None:
        settings.DEBUG = True
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())

        addresses = EmailAddress.objects.filter(verified=True, primary=True)
        assert addresses.count() == 5


class TestUrlconfRebuild:
    """allauth reads its settings when its URLconf is imported.

    A test that switches one of those settings has to rebuild the URLconf, and
    put it back afterwards so the next test starts from the demo's own.
    """

    def test_a_route_allauth_leaves_out_does_not_resolve(self, rebuild_urls) -> None:
        with (
            rebuild_urls(ACCOUNT_LOGIN_BY_CODE_ENABLED=False),
            pytest.raises(NoReverseMatch),
        ):
            reverse("account_request_login_code")

    def test_the_demos_own_urlconf_is_back_afterwards(self, rebuild_urls) -> None:
        with rebuild_urls(ACCOUNT_LOGIN_BY_CODE_ENABLED=False):
            pass

        assert reverse("account_request_login_code")


class TestDemoAccountAdapter:
    """The demo keeps phone numbers where allauth's change flow expects them."""

    def test_a_verified_change_stores_the_new_number(self, db) -> None:
        """allauth finishes a change by marking the new number verified.

        It never calls ``set_phone`` for the new number first, so marking it
        verified has to store it, or the change is confirmed on the page and
        lost from the account.
        """
        phone = PhoneNumberFactory(number="+4915112345678", verified=True)
        DemoAccountAdapter().set_phone_verified(phone.user, "+4915187654321")
        assert DemoAccountAdapter().get_phone(phone.user) == ("+4915187654321", True)


class TestOutbox:
    """The demo keeps what it would have sent, so a reviewer can follow a link.

    Sign-in by code, password reset and verification all send something. On a
    development server that would go to the console, which a reviewer opening
    the demo in a browser cannot see.
    """

    @pytest.fixture(autouse=True)
    def debug_on(self, settings):
        """The demo's development-only pages exist only with DEBUG on."""
        settings.DEBUG = True

    def test_a_sent_email_is_listed(self, client, db) -> None:
        message = EmailMessage(
            "Reset your password",
            "Follow http://testserver/accounts/password/reset/key/abc/",
            to=["regular.user@example.com"],
        )
        OutboxEmailBackend().send_messages([message])

        html = client.get(reverse("outbox")).content.decode()

        assert "Reset your password" in html
        assert 'href="http://testserver/accounts/password/reset/key/abc/"' in html

    def test_a_text_message_is_listed(self, client, db) -> None:
        user = UserFactory()
        DemoAccountAdapter().send_verification_code_sms(
            user, "+4915112345678", "ABC-123"
        )

        html = client.get(reverse("outbox")).content.decode()

        assert "+4915112345678" in html
        assert "ABC-123" in html

    def test_the_outbox_is_in_the_sidebar(self, overview_page: str) -> None:
        assert reverse("outbox") in overview_page

    def test_it_does_not_exist_without_debug(self, client, db, settings) -> None:
        settings.DEBUG = False
        assert client.get(reverse("outbox")).status_code == 404


class TestSeededStates:
    """The seeded accounts between them reach every state a page can show."""

    @pytest.fixture(autouse=True)
    def debug_on(self, settings):
        """The demo's development-only pages exist only with DEBUG on."""
        settings.DEBUG = True

    def test_staff_has_a_second_unverified_address(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())

        addresses = EmailAddress.objects.filter(user__email="staff.user@example.com")
        assert sorted((a.verified, a.primary) for a in addresses) == [
            (False, False),
            (True, True),
        ]

    def test_super_has_a_verified_phone_number(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())

        user = EmailAddress.objects.get(email="super.user@example.com").user
        number, verified = DemoAccountAdapter().get_phone(user)
        assert verified


class TestDemoTwoFactorAccount:
    """mfa.user@example.com signs in with a second factor, so the step can be seen."""

    EMAIL = "mfa.user@example.com"

    @pytest.fixture(autouse=True)
    def debug_on(self, settings):
        """The demo's development-only pages exist only with DEBUG on."""
        settings.DEBUG = True

    def test_it_has_an_authenticator_app_and_recovery_codes(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())

        user = EmailAddress.objects.get(email=self.EMAIL, verified=True).user
        types = Authenticator.objects.filter(user=user).values_list("type", flat=True)
        assert set(types) == {
            Authenticator.Type.TOTP,
            Authenticator.Type.RECOVERY_CODES,
        }

    def test_nothing_is_seeded_with_debug_off(self, db, settings) -> None:
        settings.DEBUG = False

        with pytest.raises(CommandError):
            call_command("seed_demo", stdout=StringIO())

        assert not Authenticator.objects.filter(user__email=self.EMAIL).exists()

    def test_seeding_twice_leaves_one_of_each(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())

        user = EmailAddress.objects.get(email=self.EMAIL).user
        assert Authenticator.objects.filter(user=user).count() == 2

    def test_its_secret_survives_seeding_again(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())
        user = EmailAddress.objects.get(email=self.EMAIL).user
        first = Authenticator.objects.get(user=user, type=Authenticator.Type.TOTP)
        secret = first.data["secret"]
        call_command("seed_demo", stdout=StringIO())

        again = Authenticator.objects.get(user=user, type=Authenticator.Type.TOTP)
        assert again.data["secret"] == secret

    def test_the_password_leads_to_the_second_factor_step(self, client, db) -> None:
        call_command("seed_demo", stdout=StringIO())

        response = client.post(
            reverse("account_login"), {"login": self.EMAIL, "password": "password"}
        )

        assert response["Location"] == reverse("mfa_authenticate")

    def test_the_output_names_the_account_and_the_bypass_code(
        self, db, settings
    ) -> None:
        settings.MFA_TOTP_INSECURE_BYPASS_CODE = "123456"
        output = StringIO()

        call_command("seed_demo", stdout=output)

        assert self.EMAIL in output.getvalue()
        assert "'123456' passes that step, as a demo convenience only" in (
            output.getvalue()
        )

    def test_without_a_fixed_code_the_output_says_to_compute_one(
        self, db, settings
    ) -> None:
        settings.MFA_TOTP_INSECURE_BYPASS_CODE = None
        output = StringIO()

        call_command("seed_demo", stdout=output)

        assert "no fixed code is set" in output.getvalue()


class TestDemoSocialAccounts:
    """The demo installs allauth's test provider, so a sign-in needs no credentials."""

    def test_the_test_providers_login_url_resolves(self) -> None:
        assert reverse("dummy_login")

    def test_the_suite_also_lists_github(self) -> None:
        assert reverse("github_login")


class TestSeededSocialAccounts:
    """The demo has one account that signs in with a password and one that cannot."""

    @pytest.fixture(autouse=True)
    def seeded_twice(self, db, settings):
        settings.DEBUG = True
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())

    def test_staff_has_one_connected_test_provider_account(self) -> None:
        accounts = SocialAccount.objects.filter(user__email="staff.user@example.com")

        assert [(a.provider, a.uid) for a in accounts] == [("dummy", "1001")]

    def test_social_user_signs_in_only_through_the_test_provider(self) -> None:
        user = EmailAddress.objects.get(email="social.user@example.com").user

        assert not user.has_usable_password()
        assert [(a.provider, a.uid) for a in user.socialaccount_set.all()] == [
            ("dummy", "2002")
        ]

    def test_social_user_has_one_verified_primary_address(self) -> None:
        addresses = EmailAddress.objects.filter(user__email="social.user@example.com")

        assert [(a.verified, a.primary) for a in addresses] == [(True, True)]

    def test_the_closing_output_names_both_uids_and_no_shared_password(
        self, settings
    ) -> None:
        out = StringIO()
        call_command("seed_demo", stdout=out)

        text = out.getvalue()
        assert "1001" in text
        assert "2002" in text
        assert "All three sign in with the password" not in text


class TestDemoTwoFactor:
    """The demo installs allauth's multi-factor app with every page reachable."""

    def test_the_two_factor_overview_resolves(self) -> None:
        assert reverse("mfa_index")

    def test_the_suite_never_accepts_a_fixed_code(self, settings) -> None:
        """Every test enters a real code computed from the secret."""
        assert settings.MFA_TOTP_INSECURE_BYPASS_CODE is None

    def test_the_demo_turns_on_every_factor_but_passkey_sign_up(self) -> None:
        assert demo_settings.MFA_SUPPORTED_TYPES == [
            "totp",
            "recovery_codes",
            "webauthn",
        ]
        assert demo_settings.MFA_PASSKEY_LOGIN_ENABLED
        assert demo_settings.MFA_TRUST_ENABLED
        assert not getattr(demo_settings, "MFA_PASSKEY_SIGNUP_ENABLED", False)


class TestDemoUserSessions:
    """The demo installs allauth's user sessions app so the sessions page exists."""

    def test_the_sessions_page_resolves(self) -> None:
        assert reverse("usersessions_list")


class TestSeededSessions:
    """regular.user is signed in from two other browsers, and nobody else is."""

    @pytest.fixture(autouse=True)
    def debug_on(self, settings):
        """The demo's development-only pages exist only with DEBUG on."""
        settings.DEBUG = True

    def test_seeding_twice_leaves_exactly_two_sessions_for_regular_user(
        self, db
    ) -> None:
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())

        user = EmailAddress.objects.get(email="regular.user@example.com").user
        sessions = UserSession.objects.filter(user=user)
        assert sorted(session.ip for session in sessions) == [
            "192.0.2.10",
            "198.51.100.24",
        ]
        assert all(session.user_agent for session in sessions)
        assert Session.objects.count() == 2

    def test_allauth_keeps_both_when_it_lists_them(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())

        user = EmailAddress.objects.get(email="regular.user@example.com").user
        assert len(UserSession.objects.purge_and_list(user)) == 2

    def test_no_other_account_has_a_session(self, db) -> None:
        call_command("seed_demo", stdout=StringIO())

        user = EmailAddress.objects.get(email="regular.user@example.com").user
        assert not UserSession.objects.exclude(user=user).exists()

    def test_the_output_describes_them_without_a_session_key(self, db) -> None:
        out = StringIO()
        call_command("seed_demo", stdout=out)

        assert "regular.user@example.com" in out.getvalue()
        assert "two other browsers" in out.getvalue()
        assert not any(
            key in out.getvalue()
            for key in Session.objects.values_list("session_key", flat=True)
        )


class TestSeededSessionsWalkthrough:
    """Signing in as regular.user shows the seeded sessions and the action."""

    def test_signing_in_lists_three_sessions_and_offers_to_sign_out_the_others(
        self, client, db, settings
    ) -> None:
        settings.DEBUG = True
        call_command("seed_demo", stdout=StringIO())
        client.post(
            reverse("account_login"),
            {"login": "regular.user@example.com", "password": "password"},
        )

        html = client.get(reverse("usersessions_list")).content.decode()

        assert html.count("<tbody") == 1
        assert html.split("<tbody", 1)[1].count("<tr") == 3
        assert "Sign Out Other Sessions" in html
