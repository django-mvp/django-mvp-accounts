"""The mirror of ``mvp_accounts/tokens/forms.py``: the lifetime a person chooses."""

from datetime import timedelta

import pytest

from mvp_accounts.tokens.forms import CreateTokenForm


class TestCreateTokenForm:
    @pytest.mark.parametrize(
        ("choice", "expiry"),
        [
            ("7d", timedelta(days=7)),
            ("30d", timedelta(days=30)),
            ("90d", timedelta(days=90)),
            ("1y", timedelta(days=365)),
            ("never", None),
        ],
    )
    def test_each_choice_gives_its_expiry(self, choice, expiry) -> None:
        form = CreateTokenForm({"lifetime": choice})

        assert form.is_valid()
        assert form.get_expiry() == expiry

    def test_thirty_days_is_chosen_to_begin_with(self) -> None:
        assert CreateTokenForm().fields["lifetime"].initial == "30d"

    def test_a_lifetime_outside_the_list_is_refused_on_its_field(self) -> None:
        form = CreateTokenForm({"lifetime": "forever"})

        assert form.has_error("lifetime", code="invalid_choice")

    def test_a_missing_lifetime_is_refused_on_its_field(self) -> None:
        form = CreateTokenForm({})

        assert form.has_error("lifetime", code="required")
