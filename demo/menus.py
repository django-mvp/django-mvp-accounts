"""Sidebar navigation for the demo project.

The tree is registered by :meth:`demo.apps.DemoConfig.ready` importing this
module.

A page is added here in four steps: a view in ``demo/views.py``, a route in
``demo/urls.py``, a template under ``demo/templates/demo/``, and one
``MenuItem`` below. A menu entry whose ``view_name`` will not resolve is
dropped from the tree without an error, so a page that never appears in the
sidebar is usually a name that does not match the route.
"""

from flex_menu import MenuItem
from mvp.menus import AppMenu

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
    ]
)
