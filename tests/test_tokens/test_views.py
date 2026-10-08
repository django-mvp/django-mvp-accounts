"""The mirror of ``mvp_accounts/tokens/views.py``: the three tokens pages."""

from datetime import timedelta

import pytest
from django.shortcuts import resolve_url
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from tests.factories import AuthTokenFactory, UserFactory


@pytest.fixture
def token(signed_in_client):
    return AuthTokenFactory(user=signed_in_client.user)


@pytest.fixture
def page_urls(token) -> dict[str, str]:
    return {
        "list": reverse("account_api_tokens"),
        "create": reverse("account_api_token_create"),
        "revoke": reverse("account_api_token_revoke", args=[token.token_key]),
    }


@pytest.fixture(params=["list", "create", "revoke"])
def page_url(request, page_urls) -> str:
    return page_urls[request.param]


class TestTokenPages:
    def test_a_signed_in_person_gets_the_page(self, signed_in_client, page_url) -> None:
        assert signed_in_client.get(page_url).status_code == 200

    def test_the_page_is_drawn_inside_the_account_center(
        self, signed_in_client, page_url
    ) -> None:
        response = signed_in_client.get(page_url)

        assert "mvp/account/base.html" in [t.name for t in response.templates]

    def test_a_visitor_is_sent_to_sign_in(self, page_url) -> None:
        response = Client().get(page_url)

        assert response.status_code == 302
        sign_in = resolve_url("account_login")
        assert response["Location"] == f"{sign_in}?next={page_url}"


class TestTokensView:
    def test_it_renders_the_approved_list_template(self, signed_in_client) -> None:
        response = signed_in_client.get(reverse("account_api_tokens"))

        assert "mvp_accounts/tokens/list.html" in [t.name for t in response.templates]

    def test_a_row_links_to_the_revoke_page_by_token_key(
        self, signed_in_client, token
    ) -> None:
        page = signed_in_client.get(reverse("account_api_tokens")).content.decode()

        revoke = reverse("account_api_token_revoke", args=[token.token_key])
        assert f'href="{revoke}"' in page

    def test_the_create_page_is_linked(self, signed_in_client) -> None:
        page = signed_in_client.get(reverse("account_api_tokens")).content.decode()

        assert f'href="{reverse("account_api_token_create")}"' in page


class TestCreateTokenView:
    def test_it_renders_the_approved_create_template(self, signed_in_client) -> None:
        response = signed_in_client.get(reverse("account_api_token_create"))

        assert "mvp_accounts/tokens/create.html" in [t.name for t in response.templates]
        assert "form" in response.context


class TestRevokeTokenView:
    def test_it_renders_the_approved_revoke_template(
        self, signed_in_client, page_urls
    ) -> None:
        response = signed_in_client.get(page_urls["revoke"])

        assert "mvp_accounts/tokens/revoke.html" in [t.name for t in response.templates]

    def test_it_asks_about_the_token_the_address_names(
        self, signed_in_client, token, page_urls
    ) -> None:
        response = signed_in_client.get(page_urls["revoke"])

        assert response.context["token"] == token

    def test_another_persons_token_is_not_shown(self, signed_in_client, db) -> None:
        stranger = AuthTokenFactory(user=UserFactory())

        response = signed_in_client.get(
            reverse("account_api_token_revoke", args=[stranger.token_key])
        )

        assert response.status_code != 200
        assert stranger.token_key not in response.content.decode()

    def test_an_expired_token_is_not_shown(self, signed_in_client) -> None:
        expired = AuthTokenFactory(
            user=signed_in_client.user, expiry=timezone.now() - timedelta(days=1)
        )

        response = signed_in_client.get(
            reverse("account_api_token_revoke", args=[expired.token_key])
        )

        assert response.status_code != 200
        assert expired.token_key not in response.content.decode()
