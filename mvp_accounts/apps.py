from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class MvpAccountsConfig(AppConfig):
    """What a project gets when it adds this package to INSTALLED_APPS.

    The label is set explicitly rather than left to Django's default, which is
    the last segment of the module path. Two installed apps whose paths end in
    the same word collide on that default, and the error names neither of them
    clearly.
    """

    name = "mvp_accounts"
    label = "mvp_accounts"
    verbose_name = _("Accounts")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Add this package's Account Center entries when allauth is installed.

        Without allauth there is no account management to point at, and the
        module that adds the entries is never imported.
        """
        if apps.is_installed("allauth.account"):
            from mvp_accounts import menus  # noqa: F401
