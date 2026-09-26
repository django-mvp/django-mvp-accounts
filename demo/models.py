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


class SentMessage(models.Model):
    """An email or text message the demo would have sent.

    A development server would print these to the console, which a reviewer
    opening the demo in a browser cannot see. Keeping them lets the outbox
    page show the link or code a page is waiting for.
    """

    recipient = models.CharField(
        max_length=254,
        verbose_name=_("recipient"),
        help_text=_("The address or phone number it was sent to."),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_("subject"),
        help_text=_("The email's subject, or 'Text message'."),
    )
    body = models.TextField(
        verbose_name=_("body"),
        help_text=_("The message as it would have been sent."),
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("sent at"),
        help_text=_("When it was sent. The outbox lists the newest first."),
    )

    class Meta:
        ordering = ["-sent_at"]
        verbose_name = _("sent message")
        verbose_name_plural = _("sent messages")

    def __str__(self) -> str:
        return f"{self.subject} → {self.recipient}"
