"""allauth's social account pages render inside django-mvp's shell.

The pages are driven through allauth's own test provider, which completes a
sign-in on this machine. Each is asserted on what it renders, by the four
assertions the entrance pages of the account app are held to.
"""

import re

import pytest
from django.urls import reverse
from easy_icons import icon

from tests.test_entrance_pages import EntrancePageAssertions

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
    """Each provider allauth lists is one button with its icon and its name."""

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
        """The markup is what the project's icon mapping gives that id."""
        href = reverse(f"{provider_id}_login")
        [content] = [c for h, c in LOGIN_LINK.findall(page) if h == href]

        assert icon(provider_id) in content

    def test_the_buttons_are_the_shells_buttons(self, page: str) -> None:
        assert page.count('class="btn ') >= 2
        assert "<ul>" not in page

    def test_no_provider_leaves_no_button_and_no_heading(
        self, client, db, settings
    ) -> None:
        settings.SOCIALACCOUNT_ADAPTER = "tests.adapters.NoProvidersSocialAdapter"

        for name in ("account_login", "account_signup"):
            html = client.get(reverse(name)).content.decode()

            assert not LOGIN_LINK.findall(html)
            assert "Or use a third-party" not in html
            assert "<hr" not in html
