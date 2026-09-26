"""The entries this package adds to django-mvp's Account Center navigation.

django-flex-menus imports the ``menus`` module of every installed app when it
starts, so this module cannot rely on being imported only when it is wanted.
It adds its "Account" group only when allauth is installed, so a project
without it never builds entries that could only be dropped again. An entry
whose page allauth has not routed, the phone number page with phone numbers
turned off, is left out of the rendered menu by django-mvp itself, so nothing
here checks settings.
"""

from django.apps import apps
from django.utils.translation import gettext_lazy as _

if apps.is_installed("allauth"):
    from flex_menu import MenuItem
    from mvp.menus import AccountCenterMenu, MenuGroup

    AccountCenterMenu.append(
        MenuGroup(
            name="account",
            extra_context={"label": _("Account")},
            children=[
                MenuItem(
                    name="email",
                    view_name="account_email",
                    extra_context={"label": _("Email"), "icon": "email"},
                ),
                MenuItem(
                    name="password",
                    view_name="account_change_password",
                    extra_context={"label": _("Password"), "icon": "password"},
                ),
                MenuItem(
                    name="phone",
                    view_name="account_change_phone",
                    extra_context={"label": _("Phone number"), "icon": "phone"},
                ),
            ],
        )
    )
