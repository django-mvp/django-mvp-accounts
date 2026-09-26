from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PhoneNumber(models.Model):
    """A person's phone number, kept for the demo's account adapter."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_number",
        verbose_name=_("user"),
        help_text=_("The account this number belongs to."),
    )
    number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name=_("number"),
        help_text=_("The number in international format, for example +4915112345678."),
    )
    verified = models.BooleanField(
        default=False,
        verbose_name=_("verified"),
        help_text=_("Whether the person has entered the code sent to this number."),
    )

    class Meta:
        verbose_name = _("phone number")
        verbose_name_plural = _("phone numbers")

    def __str__(self) -> str:
        return self.number
