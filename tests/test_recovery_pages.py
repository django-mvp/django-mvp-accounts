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
