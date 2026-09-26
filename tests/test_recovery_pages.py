"""allauth's recovery pages render as entrance pages.

Password reset and email verification are pages a person opens from a link in
their mail, usually not signed in, so they are entrance pages like sign-in.
Each is asserted on what it renders, by the same four checks as the sign-in and
sign-up pages.
"""

import re

from django.core import mail
from django.urls import reverse

from tests.factories import EmailAddressFactory
from tests.test_entrance_pages import EntrancePageAssertions

LINK = re.compile(r"https?://[^/\s]+(/\S+)")
CODE = re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}$", re.MULTILINE)
NEW_PASSWORD = "a-long-unusual-passphrase"


def first_link_in_mail() -> str:
    """The path of the first link in the newest message in the outbox."""
    return LINK.search(mail.outbox[-1].body).group(1)


class TestPasswordResetByLink(EntrancePageAssertions):
    def test_request_page(self, client, db) -> None:
        response = client.get(reverse("account_reset_password"))

        self.assert_entrance_page(response, 'name="email"')

    def test_check_your_email_page(self, client, db) -> None:
        address = EmailAddressFactory()

        response = client.post(
            reverse("account_reset_password"), {"email": address.email}, follow=True
        )

        self.assert_entrance_page(response, "We have sent you an email")

    def test_new_password_page_from_the_emailed_link(self, client, db) -> None:
        address = EmailAddressFactory()
        client.post(reverse("account_reset_password"), {"email": address.email})

        response = client.get(first_link_in_mail(), follow=True)

        self.assert_entrance_page(response, 'name="password1"')

    def test_password_changed_page(self, client, db) -> None:
        address = EmailAddressFactory()
        client.post(reverse("account_reset_password"), {"email": address.email})
        form_page = client.get(first_link_in_mail(), follow=True)

        response = client.post(
            form_page.request["PATH_INFO"],
            {"password1": NEW_PASSWORD, "password2": NEW_PASSWORD},
            follow=True,
        )

        self.assert_entrance_page(response, "Your password is now changed.")

    def test_invalid_link_page(self, client, db) -> None:
        response = client.get(
            reverse("account_reset_password_from_key", args=["abc", "not-a-token"])
        )

        html = self.assert_entrance_page(response, "Bad Token")
        assert 'name="password1"' not in html

    def test_used_link_page(self, client, db) -> None:
        address = EmailAddressFactory()
        client.post(reverse("account_reset_password"), {"email": address.email})
        link = first_link_in_mail()
        form_page = client.get(link, follow=True)
        client.post(
            form_page.request["PATH_INFO"],
            {"password1": NEW_PASSWORD, "password2": NEW_PASSWORD},
        )

        response = client.get(link, follow=True)

        html = self.assert_entrance_page(response, "Bad Token")
        assert 'name="password1"' not in html


def code_in_mail() -> str:
    """The code in the newest message in the outbox."""
    return CODE.search(mail.outbox[-1].body).group(0)


class TestPasswordResetByCode(EntrancePageAssertions):
    def test_code_page(self, client, db, rebuild_urls) -> None:
        address = EmailAddressFactory()

        with rebuild_urls(ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED=True):
            response = client.post(
                reverse("account_reset_password"),
                {"email": address.email},
                follow=True,
            )

        self.assert_entrance_page(response, 'name="code"')

    def test_new_password_page_after_the_code(self, client, db, rebuild_urls) -> None:
        address = EmailAddressFactory()

        with rebuild_urls(ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED=True):
            client.post(reverse("account_reset_password"), {"email": address.email})
            response = client.post(
                reverse("account_confirm_password_reset_code"),
                {"code": code_in_mail()},
                follow=True,
            )

        self.assert_entrance_page(response, 'name="password1"')

    def test_request_page_offers_no_code_when_the_project_turns_it_off(
        self, client, db
    ) -> None:
        response = client.get(reverse("account_reset_password"))

        html = self.assert_entrance_page(response, 'name="email"')
        assert not re.search(r"\bcode\b", html, re.IGNORECASE)


class TestEmailVerification(EntrancePageAssertions):
    def sign_up(self, client, email: str):
        """Sign up as ``email``.

        allauth rate-limits mail per address in the cache, which outlives a
        test, so each test signs up as an address of its own.
        """
        return client.post(
            reverse("account_signup"),
            {
                "email": email,
                "password1": NEW_PASSWORD,
                "password2": NEW_PASSWORD,
            },
            follow=True,
        )

    def test_verification_sent_page(self, client, db) -> None:
        response = self.sign_up(client, "sent@example.com")

        self.assert_entrance_page(response, "Verify Your Email Address")

    def test_confirmation_page_from_the_emailed_link(self, client, db) -> None:
        self.sign_up(client, "confirm@example.com")

        response = client.get(first_link_in_mail(), follow=True)

        self.assert_entrance_page(response, "Confirm Email Address")

    def test_verified_email_required_page(self, client, db) -> None:
        address = EmailAddressFactory(verified=False)
        client.force_login(address.user)

        response = client.get(reverse("members_only"))

        html = self.assert_entrance_page(response, "Verify Your Email Address")
        assert reverse("account_email") in html

    def test_code_page(self, client, db, rebuild_urls) -> None:
        with rebuild_urls(ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True):
            response = self.sign_up(client, "code@example.com")

        self.assert_entrance_page(response, 'name="code"')

    def test_no_code_is_offered_when_verification_is_by_link(self, client, db) -> None:
        """The demo verifies by link, so nothing on the page asks for a code."""
        response = self.sign_up(client, "link@example.com")

        html = self.assert_entrance_page(response, "Verify Your Email Address")
        assert 'name="code"' not in html
