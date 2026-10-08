"""The mirror of ``mvp_accounts/tokens/urls.py``: the routes a project includes."""

import pytest
from django.urls import resolve, reverse

from mvp_accounts.tokens import views


class TestTokenRoutes:
    @pytest.mark.parametrize(
        ("name", "args"),
        [
            ("account_api_tokens", []),
            ("account_api_token_create", []),
            ("account_api_token_revoke", ["tok_abc123"]),
        ],
    )
    def test_each_route_name_reverses(self, name, args) -> None:
        assert reverse(name, args=args)

    def test_the_revoke_route_takes_a_token_key_with_a_slash_in_it(self) -> None:
        url = reverse("account_api_token_revoke", args=["acme/abc123"])

        assert resolve(url).kwargs == {"token_key": "acme/abc123"}

    @pytest.mark.parametrize(
        ("name", "args", "view"),
        [
            ("account_api_tokens", [], views.TokensView),
            ("account_api_token_create", [], views.CreateTokenView),
            ("account_api_token_revoke", ["tok_abc123"], views.RevokeTokenView),
        ],
    )
    def test_each_route_reaches_its_view(self, name, args, view) -> None:
        assert resolve(reverse(name, args=args)).func.view_class is view
