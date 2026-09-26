"""allauth's connected accounts page renders inside django-mvp's shell.

The page is asserted on what it renders, by the four assertions the account
management pages are held to. The subject is a template,
``socialaccount/connections.html``, so this module does not mirror a source
file.
"""

import re

import pytest
from django.test import override_settings
from django.urls import reverse

from tests.factories import EmailAddressFactory, SocialAccountFactory, UserFactory
from tests.test_management_pages import ManagementPageAssertions

CONNECTIONS = reverse("socialaccount_connections")
CONNECT_LINK = re.compile(r'href="(/accounts/dummy/login/)\?[^"]*process=connect')
NO_PASSWORD = "Your account has no password set up."
REQUIRED = "This field is required."
# Connecting and disconnecting are sensitive, so allauth asks for a recent
# sign-in, which ``force_login`` does not record.
NO_REAUTHENTICATION = override_settings(ACCOUNT_REAUTHENTICATION_REQUIRED=False)


@pytest.fixture
def person(client, db):
    """A signed-in account with a password and a verified address."""
    address = EmailAddressFactory()
    client.force_login(address.user)
    return address.user


@pytest.fixture
def passwordless(client, db):
    """A signed-in account with no password, whose one account is its way in."""
    address = EmailAddressFactory(user=UserFactory(password=None))
    client.force_login(address.user)
    return address.user


class TestConnectionsPage(ManagementPageAssertions):
    def test_a_connected_account_is_listed_with_a_remove_action(
        self, client, person
    ) -> None:
        account = SocialAccountFactory(user=person)

        response = client.get(CONNECTIONS)

        html = self.assert_management_page(response, 'name="account"')
        assert f'value="{account.pk}"' in html
        assert "Remove" in html

    def test_the_provider_buttons_connect_rather_than_sign_in(
        self, client, person
    ) -> None:
        html = client.get(CONNECTIONS).content.decode()

        assert CONNECT_LINK.search(html)

    def test_the_connect_buttons_stack_at_full_width(self, client, person) -> None:
        """A management page carries the shell's ``collapse`` context, which
        must not turn the list into a row on wide screens."""
        html = client.get(CONNECTIONS).content.decode()
        before = html[: CONNECT_LINK.search(html).start()]
        button = before.rsplit("<a ", 1)[1]
        container = before.rsplit("<div ", 1)[1].split(">", 1)[0]

        assert "btn-block" in button
        assert "flex-col" in container
        assert "flex-row" not in container

    def test_with_none_connected_it_says_so_and_offers_the_buttons(
        self, client, person
    ) -> None:
        response = client.get(CONNECTIONS)

        html = self.assert_management_page(response, "Add a Third-Party Account")
        assert "no third-party accounts connected" in html
        assert 'name="account"' not in html
        assert CONNECT_LINK.search(html)

    def test_it_is_an_entry_in_the_account_center_menu(self, client, person) -> None:
        html = client.get(CONNECTIONS).content.decode()

        assert f'href="{CONNECTIONS}"' in html


class TestRefusals(ManagementPageAssertions):
    """allauth's errors reach the page, in an alert above its markup."""

    def test_the_only_way_to_sign_in_is_not_removed(self, client, passwordless) -> None:
        account = SocialAccountFactory(user=passwordless)

        response = client.post(CONNECTIONS, {"account": account.pk})

        html = self.assert_management_page(response, 'name="account"')
        assert NO_PASSWORD in html
        passwordless.socialaccount_set.get(pk=account.pk)

    def test_an_empty_post_shows_the_required_field_message(
        self, client, person
    ) -> None:
        SocialAccountFactory(user=person)

        response = client.post(CONNECTIONS, {})

        html = self.assert_management_page(response, 'name="account"')
        assert REQUIRED in html

    def test_a_page_with_no_errors_has_no_alert(self, client, person) -> None:
        SocialAccountFactory(user=person)

        html = client.get(CONNECTIONS).content.decode()

        assert 'role="alert"' not in html


class TestConnecting(ManagementPageAssertions):
    @NO_REAUTHENTICATION
    def test_connecting_through_the_test_provider_lists_the_account(
        self, client, person
    ) -> None:
        button = client.get(CONNECTIONS).content.decode()
        [path] = CONNECT_LINK.findall(button)

        confirm = client.post(path, {"process": "connect"})
        assert confirm.status_code == 302
        client.post(confirm["location"], {"id": "7007"}, follow=True)
        response = client.get(CONNECTIONS)

        html = self.assert_management_page(response, 'name="account"')
        connected = person.socialaccount_set.get(uid="7007")
        assert f'value="{connected.pk}"' in html

    @NO_REAUTHENTICATION
    def test_a_disconnect_redirects_and_says_so(self, client, person) -> None:
        account = SocialAccountFactory(user=person)

        response = client.post(CONNECTIONS, {"account": account.pk}, follow=True)

        assert response.redirect_chain[-1][0] == CONNECTIONS
        html = self.assert_management_page(response, "Add a Third-Party Account")
        assert "The third-party account has been disconnected." in html
        assert not person.socialaccount_set.exists()
