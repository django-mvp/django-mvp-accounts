"""What appears on the Account Center page and in the shell's user menu.

The subject is a template, ``mvp/account/overview.html``, so this module does
not mirror a source file.
"""

import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from tests.factories import UserFactory
from tests.settings import BASE_DIR

WITHOUT_PHONE = ["email*", "password1*", "password2*"]
CHAINED_CARD_DIR = BASE_DIR / "tests" / "templates_chained_card"

CARDS = {
    "Email": "account_email",
    "Password": "account_change_password",
    "Phone number": "account_change_phone",
    "Connected accounts": "socialaccount_connections",
    "Sessions": "usersessions_list",
    "API tokens": "account_api_tokens",
}


def cards_of(page: str) -> str:
    """The part of the page that holds the cards."""
    start = page.index('id="account-center-cards"')
    return page[start:]


def card_count(page: str) -> int:
    """How many cards the page holds."""
    grid = BeautifulSoup(page, "html.parser").find(id="account-center-cards")
    return len(grid.find_all(recursive=False))


@pytest.fixture
def account_center(signed_in_client) -> str:
    return signed_in_client.get(reverse("account-center")).content.decode()


class TestOverviewCards:
    @pytest.mark.parametrize(("title", "url_name"), CARDS.items())
    def test_each_management_page_has_a_card(
        self, account_center, title, url_name
    ) -> None:
        cards = cards_of(account_center)
        assert f'href="{reverse(url_name)}"' in cards

    def test_no_phone_card_when_phone_numbers_are_off(
        self, signed_in_client, rebuild_urls
    ) -> None:
        with rebuild_urls(ACCOUNT_SIGNUP_FIELDS=WITHOUT_PHONE):
            page = signed_in_client.get(reverse("account-center")).content.decode()

        cards = cards_of(page)
        assert f'href="{reverse("account_email")}"' in cards
        assert f'href="{reverse("account_change_password")}"' in cards
        assert f'href="{reverse("account_change_phone")}"' not in cards

    def test_no_api_tokens_card_when_the_tokens_urls_are_not_included(
        self, signed_in_client, account_center, settings
    ) -> None:
        tokens_link = f'href="{reverse("account_api_tokens")}"'
        cards_with_tokens = cards_of(account_center)
        settings.ROOT_URLCONF = "tests.urls_without_knox"

        page = signed_in_client.get(reverse("account-center")).content.decode()

        assert tokens_link in cards_with_tokens
        assert tokens_link not in cards_of(page)
        assert card_count(page) == card_count(account_center) - 1

    def test_the_two_factor_card_links_to_the_overview(self, account_center) -> None:
        cards = cards_of(account_center)

        assert f'href="{reverse("mfa_index")}"' in cards

    def test_a_signed_out_visitor_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(reverse("account-center"))
        assert response.status_code == 302
        assert reverse("account_login") in response["Location"]


class TestOverviewCardsForAPersonTheProjectTurnsAway:
    @pytest.fixture(autouse=True)
    def staff_only(self, settings) -> None:
        settings.MVP_ACCOUNTS_API_TOKEN_ACCESS = "tests.access.staff_only"

    def test_there_is_no_api_tokens_card_for_a_person_who_is_not_staff(
        self, account_center
    ) -> None:
        cards = cards_of(account_center)

        assert f'href="{reverse("account_api_tokens")}"' not in cards
        assert f'href="{reverse("account_email")}"' in cards

    def test_a_staff_person_has_the_card(self, client, db) -> None:
        client.force_login(UserFactory(is_staff=True))

        page = client.get(reverse("account-center")).content.decode()

        assert f'href="{reverse("account_api_tokens")}"' in cards_of(page)


class TestChainedCard:
    def test_another_apps_card_shows_beside_this_packages(
        self, signed_in_client
    ) -> None:
        dirs = [CHAINED_CARD_DIR, *settings.TEMPLATES[0]["DIRS"]]
        templates = [{**settings.TEMPLATES[0], "DIRS": dirs}]

        with override_settings(TEMPLATES=templates):
            page = signed_in_client.get(reverse("account-center")).content.decode()

        cards = cards_of(page)
        assert 'id="chained-card"' in cards
        assert f'href="{reverse("account_email")}"' in cards
        assert f'href="{reverse("account_change_password")}"' in cards


class TestUserMenu:
    @pytest.fixture
    def page(self, signed_in_client) -> str:
        return signed_in_client.get(reverse("overview")).content.decode()

    def test_signed_in_it_links_to_the_account_center(self, page) -> None:
        link = f'href="{reverse("account-center")}"'
        assert link in page

    def test_signed_in_it_holds_a_sign_out_form(self, page) -> None:
        assert f'action="{reverse("account_logout")}"' in page
        assert 'id="logoutForm"' in page

    def test_signed_out_it_holds_neither(self, client, db) -> None:
        response = client.get(reverse("overview"))
        page = response.content.decode()

        assert response.status_code == 200
        assert f'href="{reverse("account-center")}"' not in page
        assert f'action="{reverse("account_logout")}"' not in page
