"""The entries this package adds to django-mvp's Account Center navigation."""

from django.apps import apps
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import AccountCenterMenu, MenuGroup


def signed_in_view_name(request: HttpRequest) -> str | None:
    """Return the URL name Django resolved a signed-in visitor's request to.

    A page reached signed out, such as a password reset, is an entrance page and
    belongs to no area, so it is never claimed.

    Args:
        request: The request being rendered.

    Returns:
        The resolved view name, or ``None`` when the visitor is signed out or
        the request did not resolve.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return None
    return getattr(getattr(request, "resolver_match", None), "view_name", None)


class AccountEntry(MenuItem):
    """An entry that is current on its own page and on the pages under it.

    django-mvp draws the Account Center's sidebar on a page that is not its own
    only when an entry in its menu marks that page current, and an entry
    matches one view name. allauth reaches most areas through several pages,
    such as the authenticator app's activation page below the two-factor
    overview, so each entry also names the pages that belong to it.

    Args:
        *args: Passed to ``MenuItem``.
        pages: View names of the other pages this entry is current on.
        **kwargs: Passed to ``MenuItem``.
    """

    def __init__(self, *args, pages: tuple[str, ...] = (), **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pages = pages

    def _create_request_copy(self) -> MenuItem:
        """Carry ``pages`` onto the per-request copy."""
        copy = super()._create_request_copy()
        copy.pages = self.pages
        return copy

    def match_url(self) -> bool:
        """Also mark the entry current on any of its ``pages``."""
        if not super().match_url():
            self.selected = signed_in_view_name(self.request) in self.pages
        return self.selected


class AccountGroup(MenuGroup):
    """The "Account" heading, which also claims the pages no entry owns.

    Args:
        *args: Passed to ``MenuGroup``.
        pages: View names of the pages that belong to no single entry.
        **kwargs: Passed to ``MenuGroup``.
    """

    def __init__(self, *args, pages: tuple[str, ...] = (), **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pages = pages

    def process(self, request, **kwargs) -> MenuItem:
        """Also mark the group current on any of its ``pages``."""
        processed = super().process(request, **kwargs)
        if processed.visible and signed_in_view_name(request) in self.pages:
            processed.selected = True
        return processed


# django-flex-menus imports every app's menus module, so the group is added only
# when allauth is installed. django-mvp drops an entry whose page is not routed.
if apps.is_installed("allauth"):
    AccountCenterMenu.append(
        AccountGroup(
            name="account",
            extra_context={"label": _("Account")},
            # Confirming who you are comes before a change on any of the pages
            # below, so it belongs to the area rather than to one entry.
            pages=(
                "account_reauthenticate",
                "mfa_reauthenticate",
                "mfa_reauthenticate_webauthn",
            ),
            children=[
                AccountEntry(
                    name="email",
                    view_name="account_email",
                    extra_context={"label": _("Email"), "icon": "email"},
                ),
                AccountEntry(
                    name="password",
                    view_name="account_change_password",
                    pages=(
                        "account_set_password",
                        "account_reset_password",
                        "account_reset_password_done",
                        "account_reset_password_from_key",
                        "account_reset_password_from_key_done",
                    ),
                    extra_context={"label": _("Password"), "icon": "password"},
                ),
                AccountEntry(
                    name="phone",
                    view_name="account_change_phone",
                    pages=("account_verify_phone",),
                    extra_context={"label": _("Phone number"), "icon": "phone"},
                ),
                AccountEntry(
                    name="connections",
                    view_name="socialaccount_connections",
                    extra_context={"label": _("Connected accounts"), "icon": "link"},
                ),
                AccountEntry(
                    name="two_factor",
                    view_name="mfa_index",
                    pages=(
                        "mfa_activate_totp",
                        "mfa_deactivate_totp",
                        "mfa_view_recovery_codes",
                        "mfa_generate_recovery_codes",
                        "mfa_list_webauthn",
                        "mfa_add_webauthn",
                        "mfa_edit_webauthn",
                        "mfa_remove_webauthn",
                    ),
                    extra_context={
                        "label": _("Two-factor authentication"),
                        "icon": "lock",
                    },
                ),
                AccountEntry(
                    name="sessions",
                    view_name="usersessions_list",
                    extra_context={"label": _("Sessions"), "icon": "login"},
                ),
            ],
        )
    )
