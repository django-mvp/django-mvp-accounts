"""The API tokens entry in django-mvp's Account Center navigation."""

from django.utils.translation import gettext_lazy as _
from mvp.menus import AccountCenterMenu

# Imported first so the "Account" group, when there is one, already exists.
from mvp_accounts.menus import AccountEntry, AccountGroup
from mvp_accounts.tokens.access import may_use_tokens


def shown_to(request, **kwargs) -> bool:
    """Show the entry only to a person who may use API tokens."""
    return may_use_tokens(request.user)


entry = AccountEntry(
    name="api_tokens",
    view_name="account_api_tokens",
    pages=("account_api_token_create", "account_api_token_revoke"),
    check=shown_to,
    extra_context={"label": _("API tokens"), "icon": "key"},
)

# The entry joins the "Account" group. That group is only there when
# django-allauth is installed, so without it the entry brings the group.
group = AccountCenterMenu.get("account")
if group is None:
    AccountCenterMenu.append(
        AccountGroup(
            name="account", extra_context={"label": _("Account")}, children=[entry]
        )
    )
else:
    group.append(entry)
