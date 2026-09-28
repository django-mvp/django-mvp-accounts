"""Sidebar navigation for the demo project."""

from flex_menu import MenuItem
from mvp.menus import AppMenu

# An entry whose view_name does not resolve is dropped without an error, so a
# page missing from the sidebar usually has a name that does not match its route.
AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
        MenuItem(
            name="outbox",
            view_name="outbox",
            extra_context={"label": "Outbox", "icon": "email"},
        ),
    ]
)
