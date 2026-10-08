"""The entries this package adds to the Account Center's navigation."""

import pytest
from django.urls import reverse
from mvp.menus import AccountCenterMenu

from tests.factories import AuthTokenFactory, UserFactory

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


class TestApiTokensEntry:
    def test_it_is_an_entry(self, account_center) -> None:
        assert href("account_api_tokens") in account_center

    def test_it_is_the_last_entry_of_the_account_group(self) -> None:
        group = AccountCenterMenu.get("account")

        assert group.children[-1].name == "api_tokens"

    def test_there_is_none_when_the_tokens_urls_are_not_included(
        self, signed_in_client, settings
    ) -> None:
        tokens_link = href("account_api_tokens")
        settings.ROOT_URLCONF = "tests.urls_without_knox"

        page = signed_in_client.get(reverse("account-center")).content.decode()

        assert href("account_email") in page
        assert tokens_link not in page

    @pytest.mark.parametrize(
        "name", ["account_api_token_create", "account_api_token_revoke"]
    )
    def test_the_account_sidebar_stays_on_the_pages_under_it(
        self, signed_in_client, name
    ) -> None:
        token = AuthTokenFactory(user=signed_in_client.user)
        args = [token.token_key] if name.endswith("revoke") else []

        page = signed_in_client.get(reverse(name, args=args)).content.decode()

        assert href("account_email") in page


class TestApiTokensEntryForAPersonTheProjectTurnsAway:
    @pytest.fixture(autouse=True)
    def staff_only(self, settings) -> None:
        settings.MVP_ACCOUNTS_API_TOKEN_ACCESS = "tests.access.staff_only"

    def test_there_is_none_for_a_person_who_is_not_staff(self, account_center) -> None:
        assert href("account_api_tokens") not in account_center
        assert href("account_email") in account_center

    def test_there_is_one_for_a_staff_person(self, client, db) -> None:
        client.force_login(UserFactory(is_staff=True))

        page = client.get(reverse("account-center")).content.decode()

        assert href("account_api_tokens") in page
