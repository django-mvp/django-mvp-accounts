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
# Connecting and disconnecting are sensitive, so allauth asks for a recent
# sign-in, which ``force_login`` does not record.
NO_REAUTHENTICATION = override_settings(ACCOUNT_REAUTHENTICATION_REQUIRED=False)


@pytest.fixture
def person(client, db):
    address = EmailAddressFactory()
    client.force_login(address.user)
    return address.user


@pytest.fixture
def passwordless(client, db):
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

    def test_the_provider_buttons_connect_rather_than_sign_in(
        self, client, person
    ) -> None:
        html = client.get(CONNECTIONS).content.decode()

        assert CONNECT_LINK.search(html)

    def test_with_none_connected_it_says_so_and_offers_the_buttons(
        self, client, person
    ) -> None:
        response = client.get(CONNECTIONS)

        html = self.assert_management_page(response, "/accounts/dummy/login/")
        assert 'name="account"' not in html
        assert CONNECT_LINK.search(html)

    def test_it_is_an_entry_in_the_account_center_menu(self, client, person) -> None:
        html = client.get(CONNECTIONS).content.decode()

        assert f'href="{CONNECTIONS}"' in html


class TestRefusals(ManagementPageAssertions):
    def test_the_only_way_to_sign_in_is_not_removed(self, client, passwordless) -> None:
        account = SocialAccountFactory(user=passwordless)

        response = client.post(CONNECTIONS, {"account": account.pk})

        html = self.assert_management_page(response, 'name="account"')
        assert 'role="alert"' in html
        passwordless.socialaccount_set.get(pk=account.pk)

    def test_an_empty_post_shows_the_required_field(self, client, person) -> None:
        SocialAccountFactory(user=person)

        response = client.post(CONNECTIONS, {})

        self.assert_management_page(response, 'name="account"')
        assert response.context["form"].has_error("account", code="required")

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
        html = self.assert_management_page(response, "/accounts/dummy/login/")
        assert 'role="alert"' in html
        assert not person.socialaccount_set.exists()
