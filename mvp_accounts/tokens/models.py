"""The one thing this package stores about a token: the name a person gave it."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from knox.settings import knox_settings


class TokenName(models.Model):
    """The name a person gave one of their API tokens.

    django-rest-knox records no name, and its model is not replaced or
    subclassed here. The name sits beside the token and is deleted with it. A
    token made anywhere but the tokens page has no row.
    """

    # One row per token, so the one-to-one's unique index is the only lookup path.
    # `swappable=False` because Django would otherwise read a KNOX_TOKEN_MODEL
    # setting that a project using knox's own model never defines.
    token = models.OneToOneField(
        knox_settings.TOKEN_MODEL,
        swappable=False,
        on_delete=models.CASCADE,
        related_name="mvp_accounts_name",
        verbose_name=_("token"),
        help_text=_("The API token this name belongs to."),
    )
    # Shown beside the token and never searched or ordered by, so not indexed.
    name = models.CharField(
        max_length=64,
        verbose_name=_("name"),
        help_text=_("What the token is for, so you can recognise it later."),
    )

    class Meta:
        verbose_name = _("API token name")
        verbose_name_plural = _("API token names")

    def __str__(self) -> str:
        return self.name
