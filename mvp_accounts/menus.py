"""The entries this package adds to django-mvp's Account Center navigation.

Imported from ``MvpAccountsConfig.ready`` only when allauth's account app is
installed. An entry whose page allauth has not routed, the phone number page
with phone numbers turned off, is left out of the rendered menu by django-mvp
itself, so nothing here checks settings.
"""

from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import AccountCenterMenu

AccountCenterMenu.extend(
    [
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
    ]
)
