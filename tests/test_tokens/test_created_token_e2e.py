"""The new-token card in a real browser: what its script does on the page.

The page's markup is tested with the test client in ``test_views.py``. What needs
a browser is the card's Alpine component: the field selects the whole token when
clicked, and the button copies it.
"""

import pytest
from django.urls import reverse
from playwright.sync_api import expect

from tests.conftest import requires_browser, wait_for_alpine

pytestmark = [requires_browser, pytest.mark.django_db(transaction=True)]

TOKEN_FIELD = "#new-api-token"
COPY_BUTTON = "#new-api-token + button"


@pytest.fixture
def new_token_page(browser, live_server, client, sign_in):
    """The tokens page a person lands on after creating a token, in a browser.

    The person signs in through allauth with the test client, and the browser
    takes over that session. It then submits the create form, as a person would.
    """
    signed_in = sign_in(client)
    context = browser.new_context()
    context.add_cookies(
        [
            {
                "name": cookie.key,
                "value": cookie.value,
                "url": live_server.url,
            }
            for cookie in signed_in.cookies.values()
            if cookie.key == "sessionid"
        ]
    )
    page = context.new_page()
    page.goto(live_server.url + reverse("account_api_token_create"))
    page.locator("form button[type=submit]").click()
    page.wait_for_url("**" + reverse("account_api_tokens"))
    wait_for_alpine(page)
    yield page
    context.close()


class TestNewTokenCard:
    def test_clicking_the_token_selects_all_of_it(self, new_token_page):
        page = new_token_page
        page.locator(COPY_BUTTON).focus()

        page.locator(TOKEN_FIELD).click()

        selected = page.evaluate(
            """() => {
              const field = document.querySelector('#new-api-token');
              return field.value.length > 0
                && field.selectionStart === 0
                && field.selectionEnd === field.value.length;
            }"""
        )
        assert selected

    def test_the_copy_button_puts_the_whole_token_on_the_clipboard(
        self, new_token_page, live_server
    ):
        page = new_token_page
        page.context.grant_permissions(
            ["clipboard-read", "clipboard-write"], origin=live_server.url
        )
        token = page.locator(TOKEN_FIELD).input_value()
        status = page.get_by_role("status")
        expect(status).to_have_text("")

        page.locator(COPY_BUTTON).click()

        expect(status).not_to_have_text("")
        assert page.evaluate("() => navigator.clipboard.readText()") == token

    def test_without_the_clipboard_api_the_button_copies_the_selected_field(
        self, new_token_page
    ):
        page = new_token_page
        # A page that is not on a secure address has no navigator.clipboard.
        page.evaluate(
            """() => {
              Object.defineProperty(navigator, 'clipboard', { value: undefined });
              window.copiedText = [];
              document.execCommand = command => {
                const field = document.querySelector('#new-api-token');
                window.copiedText.push([command, document.getSelection().toString()
                  || field.value.slice(field.selectionStart, field.selectionEnd)]);
                return true;
              };
            }"""
        )
        token = page.locator(TOKEN_FIELD).input_value()

        page.locator(COPY_BUTTON).click()

        expect(page.get_by_role("status")).not_to_have_text("")
        assert page.evaluate("() => window.copiedText") == [["copy", token]]
