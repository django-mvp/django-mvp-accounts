"""A project chooses the layout its entrance pages are drawn in.

The layout is whatever `mvp_accounts/entrance/base.html` wraps around the
page's pieces. These tests put a layout of their own in that file, one that
draws each piece in a marked element, and assert which piece each control
arrives in.
"""

import copy
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

import mvp_accounts

TESTS = Path(__file__).parent
PIECES_LAYOUT = TESTS / "templates_entrance_layout"
OWN_LOGO = TESTS / "templates_entrance_logo"
PACKAGE_TEMPLATES = Path(mvp_accounts.__file__).parent / "templates"

PIECES = ("logo", "title", "providers", "content", "footer")


def use_templates(settings, *dirs: Path) -> None:
    """Put template directories ahead of every installed app's, as a project's are."""
    templates = copy.deepcopy(settings.TEMPLATES)
    templates[0]["DIRS"] = [*dirs, *templates[0]["DIRS"]]
    settings.TEMPLATES = templates


@pytest.fixture
def pieces(client, db, settings):
    use_templates(settings, PIECES_LAYOUT)

    def fetch(url_name: str) -> dict:
        html = client.get(reverse(url_name)).content.decode()
        soup = BeautifulSoup(html, "html.parser")
        return {name: soup.find(attrs={"data-piece": name}) for name in PIECES}

    return fetch


class TestProjectLayout:
    @pytest.mark.parametrize(
        "url_name",
        [
            "account_login",
            "account_signup",
            "account_reset_password",
            "account_request_login_code",
        ],
    )
    def test_every_entrance_page_is_drawn_in_it(self, pieces, url_name) -> None:
        page = pieces(url_name)

        assert page["content"].find("form") is not None

    def test_sign_in_hands_over_its_form_as_the_content(self, pieces) -> None:
        page = pieces("account_login")

        assert page["content"].find("input", attrs={"name": "login"}) is not None

    def test_sign_in_hands_over_the_ways_past_the_form_together(self, pieces) -> None:
        page = pieces("account_login")
        code = reverse("account_request_login_code")

        providers = page["providers"]
        assert providers.find(id="passkey_login") is not None
        assert providers.find("a", href=code) is not None
        assert providers.find("a", href=lambda h: h and "/dummy/login/" in h)
        assert page["content"].find(id="passkey_login") is None
        assert page["content"].find("a", href=code) is None

    def test_sign_in_hands_over_the_link_to_sign_up(self, pieces) -> None:
        page = pieces("account_login")

        assert page["footer"].find("a", href=reverse("account_signup")) is not None

    def test_sign_up_hands_over_its_form_as_the_content(self, pieces) -> None:
        page = pieces("account_signup")

        assert page["content"].find("input", attrs={"name": "password1"}) is not None

    def test_sign_up_hands_over_the_providers(self, pieces) -> None:
        page = pieces("account_signup")

        assert page["providers"].find("a", href=lambda h: h and "/dummy/login/" in h)

    def test_sign_up_hands_over_the_link_to_sign_in(self, pieces) -> None:
        page = pieces("account_signup")

        assert page["footer"].find("a", href=reverse("account_login")) is not None

    @pytest.mark.parametrize("url_name", ["account_login", "account_signup"])
    def test_a_page_taken_apart_hands_over_one_heading(self, pieces, url_name) -> None:
        page = pieces(url_name)

        assert page["title"].get_text(strip=True)
        assert page["content"].find("h1") is None

    def test_a_page_not_taken_apart_arrives_whole(self, pieces) -> None:
        page = pieces("account_reset_password")

        assert page["content"].find("h1") is not None
        assert page["content"].find("input", attrs={"name": "email"}) is not None
        for name in ("title", "providers", "footer"):
            assert not page[name].get_text(strip=True), f"{name} is not empty"

    def test_a_failed_sign_in_comes_back_in_the_layout(
        self, client, db, settings
    ) -> None:
        use_templates(settings, PIECES_LAYOUT)

        response = client.post(
            reverse("account_login"), {"login": "nobody@example.com", "password": "x"}
        )

        soup = BeautifulSoup(response.content.decode(), "html.parser")
        content = soup.find(attrs={"data-piece": "content"})
        assert response.context["form"].errors
        assert content.find("input", attrs={"name": "login"}) is not None


class TestLogo:
    def test_it_is_the_brand_logo_linking_home(self, pieces) -> None:
        page = pieces("account_login")

        link = page["logo"].find("a", href="/")
        assert link is not None
        assert link.find("img") is not None

    def test_a_project_replaces_it_by_filling_the_block(
        self, client, db, settings
    ) -> None:
        use_templates(settings, OWN_LOGO, PIECES_LAYOUT)

        html = client.get(reverse("account_login")).content.decode()

        logo = BeautifulSoup(html, "html.parser").find(attrs={"data-piece": "logo"})
        assert logo.find(id="project-logo") is not None
        assert logo.find("img") is None


class TestPackageLayout:
    """What a project gets when it writes no layout of its own."""

    @pytest.fixture
    def page(self, client, db, settings):
        use_templates(settings, PACKAGE_TEMPLATES)

        def fetch(url_name: str) -> BeautifulSoup:
            html = client.get(reverse(url_name)).content.decode()
            return BeautifulSoup(html, "html.parser")

        return fetch

    def test_sign_in_draws_every_piece(self, page) -> None:
        soup = page("account_login")

        assert soup.find("a", href="/") is not None
        assert len(soup.find_all("h1")) == 1
        assert soup.find("input", attrs={"name": "login"}) is not None
        assert soup.find(id="passkey_login") is not None
        assert soup.find("a", href=lambda h: h and "/dummy/login/" in h)
        assert soup.find("a", href=reverse("account_signup")) is not None

    def test_a_page_not_taken_apart_keeps_its_one_heading(self, page) -> None:
        soup = page("account_reset_password")

        assert len(soup.find_all("h1")) == 1
