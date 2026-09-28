"""allauth's social account pages render inside django-mvp's shell.

The pages are driven through allauth's own test provider, which completes a
sign-in on this machine. Each is asserted on what it renders, by the four
assertions the entrance pages of the account app are held to.
"""

import re

import pytest
from django.urls import reverse
from easy_icons import icon

from tests.test_entrance_pages import (
    NAVIGATION,
    STYLESHEET,
    EntrancePageAssertions,
)

PROVIDERS = {
    "github": "GitHub",
    "dummy": "Dummy",
}
# The href carries the query allauth adds, so it is captured whole and compared
# by its path.
LOGIN_LINK = re.compile(
    r'<a\b[^>]*href="(/accounts/\w+/login/)(?:\?[^"]*)?"[^>]*>(.*?)</a>', re.S
)


class TestProviderButtons(EntrancePageAssertions):
    @pytest.fixture(params=["account_login", "account_signup"])
    def page(self, request, client, db) -> str:
        return client.get(reverse(request.param)).content.decode()

    def test_a_button_for_each_provider_listed(self, page: str) -> None:
        buttons = LOGIN_LINK.findall(page)

        assert sorted(href for href, _ in buttons) == sorted(
            reverse(f"{provider_id}_login") for provider_id in PROVIDERS
        )

    @pytest.mark.parametrize("provider_id", PROVIDERS)
    def test_a_button_links_to_its_login_url_with_its_name(
        self, page: str, provider_id: str
    ) -> None:
        href = reverse(f"{provider_id}_login")
        [content] = [c for h, c in LOGIN_LINK.findall(page) if h == href]

        assert PROVIDERS[provider_id] in content

    @pytest.mark.parametrize("provider_id", PROVIDERS)
    def test_a_button_carries_the_icon_named_after_its_provider_id(
        self, page: str, provider_id: str
    ) -> None:
        href = reverse(f"{provider_id}_login")
        [content] = [c for h, c in LOGIN_LINK.findall(page) if h == href]

        assert icon(provider_id) in content

    def test_the_buttons_are_the_shells_buttons(self, page: str) -> None:
        links = re.findall(r'<a\b[^>]*href="/accounts/\w+/login/[^"]*"[^>]*>', page)

        assert len(links) == len(PROVIDERS)
        assert all('class="btn ' in link for link in links)
        assert "<ul>" not in page

    def test_no_provider_leaves_no_button_and_no_heading(
        self, client, db, settings
    ) -> None:
        settings.SOCIALACCOUNT_ADAPTER = "tests.adapters.NoProvidersSocialAdapter"

        for name in ("account_login", "account_signup"):
            html = client.get(reverse(name)).content.decode()

            assert not LOGIN_LINK.findall(html)
            assert "<hr" not in html


class TestSocialEntrancePages(EntrancePageAssertions):
    @pytest.fixture
    def authenticate_url(self, client, db) -> str:
        response = client.post(reverse("dummy_login"), {"process": "login"})
        assert response.status_code == 302
        return response["location"]

    def test_the_confirmation_page(self, client, db) -> None:
        response = client.get(reverse("dummy_login"), {"process": "login"})

        self.assert_entrance_page(
            response, "<form", template_name="socialaccount/login.html"
        )

    def test_the_test_providers_form(self, client, authenticate_url: str) -> None:
        response = client.get(authenticate_url)

        self.assert_entrance_page(response, 'name="id"')

    def test_the_extra_sign_up_step(self, client, authenticate_url: str) -> None:
        response = client.post(authenticate_url, {"id": "1001"}, follow=True)

        self.assert_entrance_page(response, 'name="email"')
        assert response.redirect_chain[-1][0] == reverse("socialaccount_signup")

    def test_the_extra_sign_up_step_shows_a_field_error(
        self, client, authenticate_url: str
    ) -> None:
        client.post(authenticate_url, {"id": "1002"})

        response = client.post(reverse("socialaccount_signup"), {"email": "not-mail"})

        self.assert_entrance_page(response, 'name="email"')
        assert response.context["form"].has_error("email", code="invalid")

    def test_the_cancelled_page(self, client, authenticate_url: str) -> None:
        response = client.post(authenticate_url, {"action": "cancel"}, follow=True)

        self.assert_entrance_page(response, f'href="{reverse("account_login")}"')
        assert response.redirect_chain[-1][0] == reverse(
            "socialaccount_login_cancelled"
        )

    def test_the_failed_page(self, client, db) -> None:
        response = client.get(reverse("socialaccount_login_error"))
        html = response.content.decode()

        assert response.status_code == 401
        assert STYLESHEET in html, "the shell's stylesheet is not on the page"
        assert NAVIGATION not in html, "an entrance page draws no navigation"

    def test_a_completed_sign_in_ends_signed_in(
        self, client, authenticate_url: str
    ) -> None:
        response = client.post(
            authenticate_url,
            {
                "id": "1003",
                "email": "social.person@example.com",
                "email_verified": "on",
            },
        )

        assert response.status_code == 302
        page = client.get(reverse("overview"))
        assert page.wsgi_request.user.is_authenticated
        assert page.wsgi_request.user.email == "social.person@example.com"


class TestSameSiteRedirectPage(EntrancePageAssertions):
    def test_it_renders_as_an_entrance_page(self, client, db, settings) -> None:
        settings.SESSION_COOKIE_SAMESITE = "Strict"
        callback = reverse("github_callback")

        response = client.get(callback)

        html = self.assert_entrance_page(response, f'href="{callback}?_redir="')
        assert (
            f'<meta http-equiv="refresh" content="0;URL=\'{callback}?_redir=\'"' in html
        )
