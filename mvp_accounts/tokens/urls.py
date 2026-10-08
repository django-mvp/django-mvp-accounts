"""Routes for the API tokens pages, included by a project that wants them."""

from django.urls import path

from mvp_accounts.tokens.views import CreateTokenView, RevokeTokenView, TokensView

urlpatterns = [
    path("", TokensView.as_view(), name="account_api_tokens"),
    path("create/", CreateTokenView.as_view(), name="account_api_token_create"),
    path(
        "<str:digest>/revoke/",
        RevokeTokenView.as_view(),
        name="account_api_token_revoke",
    ),
]
