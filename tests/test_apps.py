"""The mirror of ``mvp_accounts/apps.py``: what starting up wires into django-mvp.

``test_app.py`` covers the installed package and its components. This module
covers the one thing ``MvpAccountsConfig.ready`` does.
"""

from django.urls import reverse
from mvp.menus import AccountCenterMenu


class TestReady:
    """Starting the app adds this package's entries to the Account Center menu."""

    def test_entries_are_on_the_menu_after_startup(self) -> None:
        names = [child.name for child in AccountCenterMenu.children]
        assert {"email", "password", "phone"} <= set(names)

    def test_entries_reach_the_rendered_page(self, signed_in_client) -> None:
        page = signed_in_client.get(reverse("account-center")).content.decode()
        assert reverse("account_change_password") in page
