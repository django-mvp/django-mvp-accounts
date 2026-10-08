"""The mirror of ``mvp_accounts/tokens/views.py``: the three tokens pages."""

from datetime import timedelta
from unittest import mock

import pytest
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.sessions.models import Session
from django.db import connection
from django.shortcuts import resolve_url
from django.template.defaultfilters import date
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from knox.crypto import hash_token
from knox.models import get_token_model

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

    def test_the_page_asks_for_the_lifetime_in_a_field_of_that_name(
        self, signed_in_client
    ) -> None:
        page = signed_in_client.get(reverse("account_api_token_create")).content

        inputs = BeautifulSoup(page, "html.parser").select('input[name="lifetime"]')
        assert {field["value"] for field in inputs} == {
            "7d",
            "30d",
            "90d",
            "1y",
            "never",
        }

    def test_loading_the_page_creates_nothing(self, signed_in_client) -> None:
        signed_in_client.get(reverse("account_api_token_create"))

        assert get_token_model().objects.count() == 0

    def test_a_valid_choice_creates_one_token_for_the_person_and_returns_to_the_list(
        self, signed_in_client
    ) -> None:
        before = timezone.now()

        response = signed_in_client.post(
            reverse("account_api_token_create"), {"lifetime": "90d"}
        )

        created = get_token_model().objects.get()
        assert created.user == signed_in_client.user
        assert (
            before + timedelta(days=90)
            <= created.expiry
            <= timezone.now() + timedelta(days=90)
        )
        assert response.status_code == 302
        assert response["Location"] == reverse("account_api_tokens")

    def test_never_stores_no_expiry(self, signed_in_client) -> None:
        signed_in_client.post(
            reverse("account_api_token_create"), {"lifetime": "never"}
        )

        assert get_token_model().objects.get().expiry is None

    def test_an_invalid_choice_creates_nothing_and_shows_the_form_again(
        self, signed_in_client
    ) -> None:
        response = signed_in_client.post(
            reverse("account_api_token_create"), {"lifetime": "forever"}
        )

        assert response.status_code == 200
        assert response.context["form"].has_error("lifetime", code="invalid_choice")
        assert get_token_model().objects.count() == 0

    def test_a_return_address_in_the_request_is_ignored(self, signed_in_client) -> None:
        response = signed_in_client.post(
            reverse("account_api_token_create") + "?next=/elsewhere/",
            {"lifetime": "30d", "next": "/elsewhere/"},
        )

        assert response["Location"] == reverse("account_api_tokens")

    def test_a_visitor_cannot_create_a_token(self, db) -> None:
        url = reverse("account_api_token_create")

        response = Client().post(url, {"lifetime": "30d"})

        assert response.status_code == 302
        assert response["Location"] == f"{resolve_url('account_login')}?next={url}"
        assert get_token_model().objects.count() == 0


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

    def test_loading_the_page_deletes_nothing(
        self, signed_in_client, token, page_urls
    ) -> None:
        signed_in_client.get(page_urls["revoke"])

        assert get_token_model().objects.filter(pk=token.pk).exists()

    def test_backing_out_leaves_the_token_working(
        self, signed_in_client, token, page_urls
    ) -> None:
        page = BeautifulSoup(
            signed_in_client.get(page_urls["revoke"]).content, "html.parser"
        )

        back = page.find("a", href=page_urls["list"])
        assert back is not None
        listed = signed_in_client.get(back["href"])
        assert list(listed.context["tokens"]) == [token]


class TestRevokingAToken:
    @pytest.fixture
    def other(self, signed_in_client):
        """A second token of the same person, which must survive."""
        return AuthTokenFactory(user=signed_in_client.user)

    def test_it_deletes_that_token_and_no_other(
        self, signed_in_client, token, other, page_urls
    ) -> None:
        signed_in_client.post(page_urls["revoke"])

        assert list(get_token_model().objects.all()) == [other]

    def test_it_adds_a_success_message_and_returns_to_the_tokens_page(
        self, signed_in_client, token, page_urls
    ) -> None:
        response = signed_in_client.post(page_urls["revoke"])

        assert response.status_code == 302
        assert response["Location"] == page_urls["list"]
        added = [m.level for m in get_messages(response.wsgi_request)]
        assert added == [messages.SUCCESS]

    def test_the_page_it_returns_to_lists_the_rest(
        self, signed_in_client, token, other, page_urls
    ) -> None:
        response = signed_in_client.post(page_urls["revoke"], follow=True)

        assert list(response.context["tokens"]) == [other]

    def test_another_person_posting_to_the_address_deletes_nothing(
        self, token, page_urls
    ) -> None:
        stranger = Client()
        stranger.force_login(UserFactory())

        response = stranger.post(page_urls["revoke"])

        assert get_token_model().objects.filter(pk=token.pk).exists()
        assert response["Location"] == page_urls["list"]

    def test_a_visitor_posting_to_the_address_deletes_nothing(
        self, token, page_urls
    ) -> None:
        Client().post(page_urls["revoke"])

        assert get_token_model().objects.filter(pk=token.pk).exists()

    def test_it_deletes_only_the_newest_of_two_that_share_a_key(
        self, signed_in_client, token, page_urls
    ) -> None:
        older = AuthTokenFactory(
            user=signed_in_client.user, created=token.created - timedelta(days=1)
        )
        get_token_model().objects.filter(pk=older.pk).update(token_key=token.token_key)

        signed_in_client.post(page_urls["revoke"])

        assert list(get_token_model().objects.all()) == [older]


class TestRevokeTokenViewForATokenThatIsGone:
    """A stranger's token, an expired one and an unknown key are one response."""

    @pytest.fixture
    def gone_urls(self, signed_in_client) -> dict[str, str]:
        stranger = AuthTokenFactory(user=UserFactory())
        expired = AuthTokenFactory(
            user=signed_in_client.user, expiry=timezone.now() - timedelta(days=1)
        )
        keys = {
            "someone else's": stranger.token_key,
            "expired": expired.token_key,
            "unknown": "0" * len(stranger.token_key),
        }
        return {
            kind: reverse("account_api_token_revoke", args=[key])
            for kind, key in keys.items()
        }

    @staticmethod
    def outcome(response) -> tuple:
        """Return what a person is told: where they go and the messages added."""
        added = tuple(
            (message.level, str(message))
            for message in get_messages(response.wsgi_request)
        )
        return response.status_code, response["Location"], added

    @pytest.fixture
    def person_at(self, signed_in_client):
        """Return a function that requests a URL as the signed-in person.

        Each request gets a client of its own, so the messages one adds are not
        waiting for the next.
        """

        def request(method: str, url: str):
            client = Client()
            client.force_login(signed_in_client.user)
            return getattr(client, method)(url)

        return request

    @pytest.mark.parametrize("method", ["get", "post"])
    @pytest.mark.parametrize("kind", ["someone else's", "expired", "unknown"])
    def test_it_redirects_to_the_tokens_page_with_a_warning(
        self, person_at, gone_urls, method, kind
    ) -> None:
        response = person_at(method, gone_urls[kind])

        status, location, added = self.outcome(response)
        assert status == 302
        assert location == reverse("account_api_tokens")
        assert [level for level, _ in added] == [messages.WARNING]

    @pytest.mark.parametrize("method", ["get", "post"])
    def test_the_three_are_indistinguishable(
        self, person_at, gone_urls, method
    ) -> None:
        outcomes = {
            kind: self.outcome(person_at(method, url))
            for kind, url in gone_urls.items()
        }

        assert len(set(outcomes.values())) == 1, outcomes

    def test_submitting_deletes_nothing(self, signed_in_client, gone_urls) -> None:
        before = get_token_model().objects.count()

        for url in gone_urls.values():
            signed_in_client.post(url)

        assert get_token_model().objects.count() == before

    def test_the_tokens_page_it_returns_to_shows_the_message(
        self, signed_in_client, gone_urls
    ) -> None:
        response = signed_in_client.get(gone_urls["unknown"], follow=True)

        shown = [message.level for message in response.context["messages"]]
        assert shown == [messages.WARNING]


COOKIE = "mvp_accounts_new_token"


class TestNewTokenShownOnce:
    @pytest.fixture
    def create_url(self) -> str:
        return reverse("account_api_token_create")

    @pytest.fixture
    def list_url(self) -> str:
        return reverse("account_api_tokens")

    @pytest.fixture
    def created(self, signed_in_client, create_url):
        """Create a token as the signed-in person and return the redirect."""
        return signed_in_client.post(create_url, {"lifetime": "30d"})

    @staticmethod
    def shown_value(response) -> str | None:
        """Return what the page holds in the new token's field, if it has one."""
        field = BeautifulSoup(response.content, "html.parser").find(id="new-api-token")
        return field["value"] if field else None

    def test_following_the_redirect_shows_the_complete_value(
        self, signed_in_client, created, list_url
    ) -> None:
        response = signed_in_client.get(created["Location"])

        value = self.shown_value(response)
        record = get_token_model().objects.get()
        assert hash_token(value) == record.digest

    def test_the_context_names_the_record_just_created(
        self, signed_in_client, created
    ) -> None:
        response = signed_in_client.get(created["Location"])

        record = get_token_model().objects.get()
        assert response.context["new_token"]["token_key"] == record.token_key

    def test_the_header_prefix_is_in_the_context(
        self, signed_in_client, created, settings
    ) -> None:
        settings.REST_KNOX = {**settings.REST_KNOX, "AUTH_HEADER_PREFIX": "Bearer"}

        response = signed_in_client.get(created["Location"])

        assert response.context["header_prefix"] == "Bearer"

    def test_a_second_load_holds_the_value_nowhere(
        self, signed_in_client, created, list_url
    ) -> None:
        first = signed_in_client.get(list_url)
        value = self.shown_value(first)

        second = signed_in_client.get(list_url)

        assert value
        assert value not in second.content.decode()
        assert "new_token" not in second.context or not second.context["new_token"]

    def test_nothing_the_server_keeps_holds_the_value(
        self, signed_in_client, created, list_url
    ) -> None:
        value = self.shown_value(signed_in_client.get(list_url))

        record = get_token_model().objects.get()
        columns = [
            str(getattr(record, field.attname))
            for field in record._meta.concrete_fields
        ]
        assert not any(value in column for column in columns)
        assert record.token_key == value[: len(record.token_key)]
        assert value not in str(dict(signed_in_client.session))
        assert not any(
            value in session.session_data for session in Session.objects.all()
        )

    def test_the_redirect_sets_a_signed_cookie_for_the_tokens_page_only(
        self, created, list_url
    ) -> None:
        cookie = created.cookies[COOKIE]

        assert cookie["path"] == list_url
        assert cookie["httponly"]
        assert cookie["samesite"] == "Strict"
        assert cookie["max-age"] == 60
        assert not cookie["secure"]

    def test_the_cookie_is_secure_on_a_secure_request(
        self, signed_in_client, create_url
    ) -> None:
        response = signed_in_client.post(create_url, {"lifetime": "30d"}, secure=True)

        assert response.cookies[COOKIE]["secure"]

    def test_the_response_that_reads_the_cookie_deletes_it_from_the_same_path(
        self, signed_in_client, created, list_url
    ) -> None:
        response = signed_in_client.get(list_url)

        cookie = response.cookies[COOKIE]
        assert cookie["max-age"] == 0
        assert cookie["path"] == list_url
        assert cookie["samesite"] == "Strict"

    def test_a_tampered_cookie_shows_nothing(
        self, signed_in_client, created, list_url
    ) -> None:
        signed_in_client.cookies[COOKIE] = created.cookies[COOKIE].value + "x"

        response = signed_in_client.get(list_url)

        assert self.shown_value(response) is None
        assert not response.context["new_token"]

    def test_an_expired_cookie_shows_nothing(
        self, signed_in_client, created, list_url
    ) -> None:
        assert COOKIE in created.cookies
        later = timezone.now().timestamp() + 61
        with mock.patch("django.core.signing.time.time", return_value=later):
            response = signed_in_client.get(list_url)

        assert self.shown_value(response) is None
        assert not response.context["new_token"]

    def test_another_person_with_the_cookie_is_shown_no_value(
        self, created, list_url
    ) -> None:
        stranger_client = Client()
        stranger_client.force_login(UserFactory())
        stranger_client.cookies[COOKIE] = created.cookies[COOKIE].value

        response = stranger_client.get(list_url)

        assert self.shown_value(response) is None
        assert not response.context["new_token"]

    def test_the_tokens_page_is_not_cacheable(
        self, signed_in_client, created, list_url
    ) -> None:
        shown = signed_in_client.get(created["Location"])
        plain = signed_in_client.get(list_url)

        for response in (shown, plain):
            assert "no-store" in response["Cache-Control"]

    def test_submitting_twice_makes_two_tokens_and_reloading_makes_none(
        self, signed_in_client, create_url, list_url
    ) -> None:
        signed_in_client.post(create_url, {"lifetime": "30d"})
        signed_in_client.post(create_url, {"lifetime": "30d"})
        assert get_token_model().objects.count() == 2

        signed_in_client.get(list_url)
        signed_in_client.get(list_url)

        assert get_token_model().objects.count() == 2


class TestCreateTokenAtTheLimit:
    @pytest.fixture
    def create_url(self) -> str:
        return reverse("account_api_token_create")

    @pytest.fixture
    def at_limit(self, signed_in_client, settings):
        """A signed-in person who holds the one token the project allows."""
        settings.REST_KNOX = {**settings.REST_KNOX, "TOKEN_LIMIT_PER_USER": 1}
        return AuthTokenFactory(user=signed_in_client.user)

    @staticmethod
    def levels(response) -> list[int]:
        """Return the level of each message the response added."""
        return [message.level for message in get_messages(response.wsgi_request)]

    def test_loading_the_page_is_refused_with_an_error_and_a_redirect(
        self, signed_in_client, at_limit, create_url
    ) -> None:
        response = signed_in_client.get(create_url)

        assert response.status_code == 302
        assert response["Location"] == reverse("account_api_tokens")
        assert self.levels(response) == [messages.ERROR]

    def test_submitting_the_page_creates_nothing(
        self, signed_in_client, at_limit, create_url
    ) -> None:
        response = signed_in_client.post(create_url, {"lifetime": "30d"})

        assert get_token_model().objects.count() == 1
        assert response["Location"] == reverse("account_api_tokens")
        assert self.levels(response) == [messages.ERROR]

    def test_the_tokens_page_it_returns_to_has_no_link_to_create_one(
        self, signed_in_client, at_limit, create_url
    ) -> None:
        response = signed_in_client.get(create_url, follow=True)

        assert response.redirect_chain[-1][0] == reverse("account_api_tokens")
        page = BeautifulSoup(response.content, "html.parser")
        assert page.find("a", href=create_url) is None

    def test_an_expired_token_does_not_count(
        self, signed_in_client, at_limit, create_url
    ) -> None:
        get_token_model().objects.update(expiry=timezone.now() - timedelta(days=1))

        response = signed_in_client.post(create_url, {"lifetime": "30d"})

        assert get_token_model().objects.count() == 2
        assert response["Location"] == reverse("account_api_tokens")
        assert self.levels(response) == []

    def test_a_token_with_no_expiry_counts(
        self, signed_in_client, at_limit, create_url
    ) -> None:
        get_token_model().objects.update(expiry=None)

        signed_in_client.post(create_url, {"lifetime": "30d"})

        assert get_token_model().objects.count() == 1

    def test_without_a_limit_creating_is_never_refused(
        self, signed_in_client, settings, create_url
    ) -> None:
        settings.REST_KNOX = {**settings.REST_KNOX, "TOKEN_LIMIT_PER_USER": None}
        AuthTokenFactory.create_batch(3, user=signed_in_client.user)

        response = signed_in_client.post(create_url, {"lifetime": "30d"})

        assert get_token_model().objects.count() == 4
        assert self.levels(response) == []

    def test_another_persons_tokens_do_not_count(
        self, signed_in_client, settings, create_url
    ) -> None:
        settings.REST_KNOX = {**settings.REST_KNOX, "TOKEN_LIMIT_PER_USER": 1}
        AuthTokenFactory(user=UserFactory())

        signed_in_client.post(create_url, {"lifetime": "30d"})

        assert get_token_model().objects.filter(user=signed_in_client.user).count() == 1
