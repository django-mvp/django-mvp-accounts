from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MvpAccessControlConfig(AppConfig):
    """What a project gets when it adds this package to INSTALLED_APPS.

    The label is set explicitly rather than left to Django's default, which is
    the last segment of the module path. Two installed apps whose paths end in
    the same word collide on that default, and the error names neither of them
    clearly.
    """

    name = "mvp_access_control"
    label = "mvp_access_control"
    verbose_name = _("Access Control")
    default_auto_field = "django.db.models.BigAutoField"
