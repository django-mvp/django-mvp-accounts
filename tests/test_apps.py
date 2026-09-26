"""The mirror of ``mvp_accounts/apps.py``: what starting the app wires up.

``test_app.py`` covers the installed package and its components. The app config
adds nothing of its own; this covers what starting it leads to, which is
django-flex-menus finding ``menus.py`` and the entries reaching the menu.
"""

from django.urls import reverse
from mvp.menus import AccountCenterMenu


class TestStartup:
    """Starting the app adds this package's entries to the Account Center menu."""

    def test_entries_are_on_the_menu_after_startup(self) -> None:
        names = [child.name for child in AccountCenterMenu.children]
        assert {"email", "password", "phone"} <= set(names)

    def test_entries_reach_the_rendered_page(self, signed_in_client) -> None:
        page = signed_in_client.get(reverse("account-center")).content.decode()
        assert reverse("account_change_password") in page
