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
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.urls import NoReverseMatch, reverse

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
        assert addresses.count() == 3


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
