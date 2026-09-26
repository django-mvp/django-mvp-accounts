"""What appears on the Account Center page and in the shell's user menu.

The subject is a template, ``mvp/account/overview.html``, so this module does
not mirror a source file.
"""

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from tests.settings import BASE_DIR

WITHOUT_PHONE = ["email*", "password1*", "password2*"]
CHAINED_CARD_DIR = BASE_DIR / "tests" / "templates_chained_card"

CARDS = {
    "Email": "account_email",
    "Password": "account_change_password",
    "Phone number": "account_change_phone",
}


def cards_of(page: str) -> str:
    """The part of the page that holds the cards."""
    start = page.index('id="account-center-cards"')
    return page[start:]


@pytest.fixture
def account_center(signed_in_client) -> str:
    """The Account Center page as a signed-in person sees it."""
    return signed_in_client.get(reverse("account-center")).content.decode()


class TestOverviewCards:
    """One card per account management page, drawn only when the page exists."""

    @pytest.mark.parametrize(("title", "url_name"), CARDS.items())
    def test_each_management_page_has_a_card(
        self, account_center, title, url_name
    ) -> None:
        cards = cards_of(account_center)
        assert f"<span>{title}</span>" in cards
        assert f'href="{reverse(url_name)}"' in cards

    def test_no_phone_card_when_phone_numbers_are_off(
        self, signed_in_client, rebuild_urls
    ) -> None:
        with rebuild_urls(ACCOUNT_SIGNUP_FIELDS=WITHOUT_PHONE):
            page = signed_in_client.get(reverse("account-center")).content.decode()

        cards = cards_of(page)
        assert "<span>Email</span>" in cards
        assert "<span>Password</span>" in cards
        assert "<span>Phone number</span>" not in cards

    def test_a_signed_out_visitor_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(reverse("account-center"))
        assert response.status_code == 302
        assert reverse("account_login") in response["Location"]


class TestChainedCard:
    """Another app's overview template adds beside this package's cards (FR-007)."""

    def test_another_apps_card_shows_beside_this_packages(
        self, signed_in_client
    ) -> None:
        dirs = [CHAINED_CARD_DIR, *settings.TEMPLATES[0]["DIRS"]]
        templates = [{**settings.TEMPLATES[0], "DIRS": dirs}]

        with override_settings(TEMPLATES=templates):
            page = signed_in_client.get(reverse("account-center")).content.decode()

        cards = cards_of(page)
        assert 'id="chained-card"' in cards
        assert "<span>Email</span>" in cards
        assert "<span>Password</span>" in cards


class TestUserMenu:
    """The shell's user menu is the way to the Account Center and to sign out.

    Read off the demo's overview page: the Account Center draws its own
    navigation in place of the user menu's Account Center row.
    """

    @pytest.fixture
    def page(self, signed_in_client) -> str:
        return signed_in_client.get(reverse("overview")).content.decode()

    def test_signed_in_it_links_to_the_account_center(self, page) -> None:
        link = f'href="{reverse("account-center")}"'
        assert link in page
        assert "<span>Account Center</span>" in page

    def test_signed_in_it_holds_a_sign_out_form(self, page) -> None:
        assert f'action="{reverse("account_logout")}"' in page
        assert 'id="logoutForm"' in page

    def test_signed_out_it_holds_neither(self, client, db) -> None:
        response = client.get(reverse("overview"))
        page = response.content.decode()

        assert response.status_code == 200
        assert "<span>Account Center</span>" not in page
        assert f'action="{reverse("account_logout")}"' not in page
