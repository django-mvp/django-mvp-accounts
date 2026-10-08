"""The form on the create page: how long the new token should last."""

from datetime import timedelta

from django import forms
from django.utils.translation import gettext_lazy as _


class CreateTokenForm(forms.Form):
    """Ask how long a new API token should work.

    The choices are fixed in the package. A token that never expires is one of
    them, for a script that runs for good.
    """

    LIFETIMES = {
        "7d": (_("7 days"), timedelta(days=7)),
        "30d": (_("30 days"), timedelta(days=30)),
        "90d": (_("90 days"), timedelta(days=90)),
        "1y": (_("1 year"), timedelta(days=365)),
        "never": (_("Never expires"), None),
    }

    lifetime = forms.ChoiceField(
        label=_("Lifetime"),
        choices=[(key, label) for key, (label, _delta) in LIFETIMES.items()],
        initial="30d",
        widget=forms.RadioSelect,
    )

    def get_expiry(self) -> timedelta | None:
        """Return how long the chosen token should last.

        Returns:
            The time from now until the token stops working, or ``None`` for a
            token that never does. Only meaningful once the form is valid.
        """
        return self.LIFETIMES[self.cleaned_data["lifetime"]][1]
