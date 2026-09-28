"""allauth's entrance pages render inside django-mvp's shell.

A page that falls back to allauth's bare markup still answers 200 and still
shows its form, so the status code proves nothing. Every page is asserted on
what it renders: the shell's stylesheet, no navigation, none of allauth's own
menu, and the form the page exists for.
"""

import copy
from pathlib import Path

from django.urls import reverse

from tests.factories import EmailAddressFactory

STYLESHEET = "css/django-mvp.css"
NAVIGATION = 'aria-label="Main navigation"'


class EntrancePageAssertions:
    def assert_entrance_page(
        self, response, form_marker: str | None = None, template_name: str | None = None
    ) -> str:
        html = response.content.decode()

        assert response.status_code == 200
        assert STYLESHEET in html, "the shell's stylesheet is not on the page"
        assert NAVIGATION not in html, "an entrance page draws no navigation"
        if form_marker is not None:
            assert form_marker in html, "the page's own form is missing"
        if template_name is not None:
            assert template_name in [t.name for t in response.templates], (
                f"{template_name} did not render"
            )
        return html


class TestEntrancePages(EntrancePageAssertions):
    def test_sign_in(self, client, db) -> None:
        response = client.get(reverse("account_login"))

        html = self.assert_entrance_page(response, 'name="login"')
        assert "<title>" in html

    def test_sign_up(self, client, db) -> None:
        response = client.get(reverse("account_signup"))

        self.assert_entrance_page(response, 'name="password1"')

    def test_sign_out(self, signed_in_client) -> None:
        response = signed_in_client.get(reverse("account_logout"))

        self.assert_entrance_page(response, f'action="{reverse("account_logout")}"')

    def test_request_a_sign_in_code(self, client, db) -> None:
        response = client.get(reverse("account_request_login_code"))

        self.assert_entrance_page(response, 'name="email"')

    def test_confirm_a_sign_in_code(self, client, db) -> None:
        address = EmailAddressFactory()

        response = client.post(
            reverse("account_request_login_code"),
            {"email": address.email},
            follow=True,
        )

        self.assert_entrance_page(response, 'name="code"')

    def test_sign_up_closed(self, client, db, settings) -> None:
        settings.ACCOUNT_ADAPTER = "tests.adapters.ClosedSignupAdapter"

        response = client.get(reverse("account_signup"))

        html = self.assert_entrance_page(
            response, template_name="account/signup_closed.html"
        )
        assert 'name="password1"' not in html

    def test_account_inactive(self, client, db) -> None:
        response = client.get(reverse("account_inactive"))

        self.assert_entrance_page(
            response, template_name="account/account_inactive.html"
        )


class TestMessages(EntrancePageAssertions):
    def test_a_message_shows_on_an_entrance_page(self, client, db, settings) -> None:
        settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
        response = client.post(
            reverse("account_signup"),
            {
                "email": "new.person@example.com",
                "password1": "a-long-unusual-passphrase",
                "password2": "a-long-unusual-passphrase",
            },
            follow=True,
        )

        html = self.assert_entrance_page(
            response, template_name="account/verification_sent.html"
        )
        assert 'role="alert"' in html
        assert "new.person@example.com" in html

    def test_the_sign_out_message_shows_on_the_page_that_follows(
        self, signed_in_client
    ) -> None:
        response = signed_in_client.post(reverse("account_logout"), follow=True)

        assert 'role="alert"' in response.content.decode()


class TestWhatAProjectTurnedOff:
    def test_sign_in_offers_a_code_when_the_project_allows_it(self, client, db) -> None:
        html = client.get(reverse("account_login")).content.decode()

        assert reverse("account_request_login_code") in html

    def test_sign_in_offers_no_code_when_the_project_turns_it_off(
        self, client, db, rebuild_urls
    ) -> None:
        with rebuild_urls(ACCOUNT_LOGIN_BY_CODE_ENABLED=False):
            html = client.get(reverse("account_login")).content.decode()

        assert "/login/code/" not in html

    def test_a_closed_sign_up_adds_no_link_of_the_packages_own(
        self, client, db, settings
    ) -> None:
        signup = reverse("account_signup")
        settings.ACCOUNT_ADAPTER = "tests.adapters.ClosedSignupAdapter"

        response = client.get(reverse("account_login"))

        # The one in allauth's own sentence, "please sign up first".
        assert response.content.decode().count(signup) == 1
        closed = client.get(signup)
        assert "account/signup_closed.html" in [t.name for t in closed.templates]
        assert 'name="password1"' not in closed.content.decode()


class TestHostProjectOverride:
    def test_the_projects_sign_in_page_is_the_one_rendered(
        self, client, db, settings
    ) -> None:
        override_dir = Path(__file__).parent / "templates_host_override"
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["DIRS"] = [override_dir, *templates[0]["DIRS"]]
        settings.TEMPLATES = templates

        html = client.get(reverse("account_login")).content.decode()

        assert "This project's own sign-in page" in html
        assert 'name="login"' not in html
