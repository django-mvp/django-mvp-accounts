"""The mirror of ``mvp_accounts/tokens/views.py``: the three tokens pages."""

from datetime import timedelta

import pytest
from bs4 import BeautifulSoup
from django.db import connection
from django.shortcuts import resolve_url
from django.template.defaultfilters import date
from django.test import Client
from django.test.utils import CaptureQueriesContext
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


class TestTokensList:
    @pytest.fixture
    def list_url(self) -> str:
        return reverse("account_api_tokens")

    @staticmethod
    def row_for(page: str, token):
        """Return the table row that carries the token's ``token_key``."""
        soup = BeautifulSoup(page, "html.parser")
        rows = [
            row
            for row in soup.select("tbody tr")
            if row.find("code").get_text().startswith(token.token_key)
        ]
        assert len(rows) <= 1
        return rows[0] if rows else None

    def test_three_tokens_are_three_rows_with_their_key_and_days(
        self, signed_in_client, list_url
    ) -> None:
        now = timezone.now()
        tokens = [
            AuthTokenFactory(
                user=signed_in_client.user,
                created=now - timedelta(days=10 * number),
                expiry=now + timedelta(days=20 + number),
            )
            for number in (1, 2, 3)
        ]

        page = signed_in_client.get(list_url).content.decode()

        assert len(BeautifulSoup(page, "html.parser").select("tbody tr")) == 3
        for token in tokens:
            created, expiry = self.row_for(page, token).find_all("time")
            assert created["datetime"] == token.created.strftime("%Y-%m-%d")
            assert created.get_text() == date(token.created, "DATE_FORMAT")
            assert expiry["datetime"] == token.expiry.strftime("%Y-%m-%d")
            assert expiry.get_text() == date(token.expiry, "DATE_FORMAT")

    def test_another_persons_tokens_are_absent(
        self, signed_in_client, token, list_url
    ) -> None:
        stranger = AuthTokenFactory(user=UserFactory())

        page = signed_in_client.get(list_url).content.decode()

        assert self.row_for(page, token) is not None
        assert stranger.token_key not in page

    def test_without_tokens_there_is_no_table_and_a_link_to_create_one(
        self, signed_in_client, list_url
    ) -> None:
        page = signed_in_client.get(list_url).content.decode()

        soup = BeautifulSoup(page, "html.parser")
        assert soup.find("table") is None
        create = reverse("account_api_token_create")
        assert soup.find("a", href=create) is not None

    def test_a_token_with_no_expiry_has_no_date_in_its_expiry_cell(
        self, signed_in_client, list_url
    ) -> None:
        forever = AuthTokenFactory(user=signed_in_client.user, expiry=None)

        page = signed_in_client.get(list_url).content.decode()

        created_cell, expiry_cell = self.row_for(page, forever).find_all("td")[:2]
        assert created_cell.find("time") is not None
        assert expiry_cell.find("time") is None

    def test_an_expired_token_is_not_listed(self, signed_in_client, list_url) -> None:
        expired = AuthTokenFactory(
            user=signed_in_client.user, expiry=timezone.now() - timedelta(days=1)
        )

        page = signed_in_client.get(list_url).content.decode()

        assert expired.token_key not in page

    def test_the_page_costs_the_same_queries_for_one_token_and_several(
        self, signed_in_client, token, list_url, django_assert_num_queries
    ) -> None:
        signed_in_client.get(list_url)  # the first request also records the session
        with CaptureQueriesContext(connection) as one:
            signed_in_client.get(list_url)
        AuthTokenFactory.create_batch(3, user=signed_in_client.user)

        with django_assert_num_queries(len(one)):
            signed_in_client.get(list_url)

    def test_the_context_carries_the_limit_and_whether_it_is_reached(
        self, signed_in_client, settings, list_url
    ) -> None:
        settings.REST_KNOX = {**settings.REST_KNOX, "TOKEN_LIMIT_PER_USER": 2}
        AuthTokenFactory(user=signed_in_client.user)
        below = signed_in_client.get(list_url).context
        AuthTokenFactory(user=signed_in_client.user)
        reached = signed_in_client.get(list_url).context

        assert (below["token_limit"], below["at_limit"]) == (2, False)
        assert (reached["token_limit"], reached["at_limit"]) == (2, True)

    def test_a_project_without_a_limit_is_never_at_it(
        self, signed_in_client, settings, list_url
    ) -> None:
        settings.REST_KNOX = {**settings.REST_KNOX, "TOKEN_LIMIT_PER_USER": None}
        AuthTokenFactory.create_batch(3, user=signed_in_client.user)

        context = signed_in_client.get(list_url).context

        assert context["token_limit"] is None
        assert context["at_limit"] is False

    def test_at_the_limit_the_list_no_longer_offers_to_create_one(
        self, signed_in_client, settings, list_url
    ) -> None:
        settings.REST_KNOX = {**settings.REST_KNOX, "TOKEN_LIMIT_PER_USER": 1}
        AuthTokenFactory(user=signed_in_client.user)

        page = signed_in_client.get(list_url).content.decode()

        soup = BeautifulSoup(page, "html.parser")
        assert soup.find("a", href=reverse("account_api_token_create")) is None


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
