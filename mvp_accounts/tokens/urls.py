"""Routes for the API tokens page, included by a project that wants it."""

from django.urls import path

from mvp_accounts.tokens.views import RevokeTokenView, TokensView

urlpatterns = [
    path("", TokensView.as_view(), name="account_api_tokens"),
    path(
        "<str:digest>/revoke/",
        RevokeTokenView.as_view(),
        name="account_api_token_revoke",
    ),
]
