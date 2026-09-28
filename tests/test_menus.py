"""The entries this package adds to the Account Center's navigation."""

import pytest
from django.urls import reverse

WITHOUT_PHONE = ["email*", "password1*", "password2*"]

ENTRIES = {
    "email": "account_email",
    "password": "account_change_password",
    "phone": "account_change_phone",
    "connections": "socialaccount_connections",
}


def href(name: str) -> str:
    return f'href="{reverse(name)}"'


@pytest.fixture
def account_center(signed_in_client) -> str:
    return signed_in_client.get(reverse("account-center")).content.decode()


class TestAccountCenterMenuEntries:
    @pytest.mark.parametrize("name", ENTRIES.values())
    def test_each_management_page_is_an_entry(self, account_center, name) -> None:
        assert href(name) in account_center

    def test_no_phone_entry_when_phone_numbers_are_off(
        self, signed_in_client, rebuild_urls
    ) -> None:
        with rebuild_urls(ACCOUNT_SIGNUP_FIELDS=WITHOUT_PHONE):
            page = signed_in_client.get(reverse("account-center")).content.decode()

        assert href("account_email") in page
        assert href("account_change_password") in page
        assert href("account_change_phone") not in page


class TestTwoFactorEntry:
    def test_it_links_to_the_overview(self, account_center) -> None:
        assert href("mfa_index") in account_center


class TestSessionsEntry:
    def test_it_is_an_entry(self, account_center) -> None:
        assert href("usersessions_list") in account_center
