"""App configuration for the API tokens page."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MvpAccountsTokensConfig(AppConfig):
    """What a project gets when it adds ``mvp_accounts.tokens`` to INSTALLED_APPS.

    Adding it is what turns API tokens on. A project that leaves it out imports
    nothing from django-rest-knox or Django REST framework.
    """

    name = "mvp_accounts.tokens"
    label = "mvp_accounts_tokens"
    verbose_name = _("API tokens")
    default_auto_field = "django.db.models.BigAutoField"
