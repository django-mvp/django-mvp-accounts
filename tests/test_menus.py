"""The entries this package adds to the Account Center's navigation."""

import re

import pytest
from django.urls import reverse

WITHOUT_PHONE = ["email*", "password1*", "password2*"]

ENTRIES = {
    "email": "account_email",
    "password": "account_change_password",
    "phone": "account_change_phone",
}


def href(name: str) -> str:
    return f'href="{reverse(name)}"'


@pytest.fixture
def account_center(signed_in_client) -> str:
    """The Account Center page as a signed-in person sees it."""
    return signed_in_client.get(reverse("account-center")).content.decode()


class TestAccountCenterMenuEntries:
    """What the Account Center's sidebar offers for account management."""

    @pytest.mark.parametrize("name", ENTRIES.values())
    def test_each_management_page_is_an_entry(self, account_center, name) -> None:
        assert href(name) in account_center

    @pytest.mark.parametrize("label", ["Email", "Password", "Phone number"])
    def test_entries_carry_their_labels(self, account_center, label) -> None:
        assert f"<span>{label}</span>" in account_center

    @pytest.mark.parametrize("icon", ["envelope", "key", "telephone"])
    def test_entries_carry_their_icons(self, account_center, icon) -> None:
        assert f'<i class="bi bi-{icon}"' in account_center

    def test_no_phone_entry_when_phone_numbers_are_off(
        self, signed_in_client, rebuild_urls
    ) -> None:
        with rebuild_urls(ACCOUNT_SIGNUP_FIELDS=WITHOUT_PHONE):
            page = signed_in_client.get(reverse("account-center")).content.decode()

        assert href("account_email") in page
        assert href("account_change_password") in page
        assert "<span>Phone number</span>" not in page
        assert href("account_change_phone") not in page


class TestAccountGroup:
    """The entries sit under one "Account" heading, never a collapsible group."""

    HEADING = re.compile(r'<li class="menu-title[^"]*">\s*<span>Account</span>')

    def test_the_entries_are_headed_account(self, account_center) -> None:
        heading = self.HEADING.search(account_center)

        assert heading is not None
        for name in ENTRIES.values():
            assert account_center.index(href(name)) > heading.end()

    def test_the_group_does_not_collapse(self, account_center) -> None:
        assert "<details" not in account_center
