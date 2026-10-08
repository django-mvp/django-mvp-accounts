"""The form a person fills in to create an API token."""

from datetime import timedelta

from django import forms
from django.utils.translation import gettext_lazy as _

# How long a token may last, as the choice a person sees.
LIFETIMES = [
    ("7", _("7 days")),
    ("30", _("30 days")),
    ("90", _("90 days")),
    ("365", _("1 year")),
    ("never", _("Never expires")),
]
DEFAULT_LIFETIME = "30"


class CreateTokenForm(forms.Form):
    """How long the new token lasts."""

    lifetime = forms.ChoiceField(
        label=_("Expires after"),
        choices=LIFETIMES,
        initial=DEFAULT_LIFETIME,
        help_text=_(
            "A token that expires limits the harm if it leaks. "
            "You can revoke any token sooner."
        ),
    )

    def get_expiry(self) -> timedelta | None:
        """Return the chosen lifetime, or ``None`` for a token that never expires."""
        lifetime = self.cleaned_data["lifetime"]
        return None if lifetime == "never" else timedelta(days=int(lifetime))
