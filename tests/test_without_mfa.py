"""What this package does in a project that keeps allauth without its multi-factor app.

It runs in a subprocess under ``tests/settings_without_mfa.py``: which apps are
installed is decided when Django starts, so the running suite cannot remove one.
The subject is that startup, so the module mirrors no source file.
"""

import textwrap

import pytest

SCRIPT = textwrap.dedent(
    """
    import json

    import django

    django.setup()

    from django.apps import apps
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from django.test import Client
    from django.urls import reverse

    import mvp_accounts  # noqa: F401

    call_command("migrate", verbosity=0)
    user = get_user_model().objects.create_user("person", password="password")
    client = Client()
    client.force_login(user)

    account_center = client.get(reverse("account-center"))
    password = client.get(reverse("account_change_password"))
    client.logout()
    sign_in = client.get(reverse("account_login"))

    print(json.dumps({
        "mfa_installed": apps.is_installed("allauth.mfa"),
        "account_center": [account_center.status_code, account_center.content.decode()],
        "password": [password.status_code, password.content.decode()],
        "sign_in": [sign_in.status_code, sign_in.content.decode()],
    }))
    """
)


@pytest.fixture(scope="module")
def result(run_in_subprocess) -> dict:
    """Start Django with allauth but no multi-factor app and render the pages."""
    return run_in_subprocess("tests.settings_without_mfa", SCRIPT)


class TestWithoutMultiFactor:
    """A project that installs allauth's account app and not its multi-factor one."""

    def test_the_subprocess_really_runs_without_the_multi_factor_app(
        self, result
    ) -> None:
        assert not result["mfa_installed"]

    def test_the_account_center_renders_and_still_offers_the_account_pages(
        self, result
    ) -> None:
        status, page = result["account_center"]
        assert status == 200
        assert "Manage email" in page
        assert "Change password" in page

    def test_the_account_center_has_no_two_factor_entry_or_card(self, result) -> None:
        _status, page = result["account_center"]
        assert "Two-factor authentication" not in page
        assert "Manage two-factor authentication" not in page

    def test_a_management_page_renders_with_no_two_factor_entry(self, result) -> None:
        status, page = result["password"]
        assert status == 200
        assert "Two-factor authentication" not in page

    def test_the_sign_in_page_renders_without_a_passkey_button(self, result) -> None:
        status, page = result["sign_in"]
        assert status == 200
        assert "passkey_login" not in page


class TestTheSubprocessCanFail:
    """Pointed at the suite's own settings, the same script sees the entry.

    Without this, a script that never looked at the multi-factor app at all
    would pass the tests above for the wrong reason.
    """

    def test_with_the_multi_factor_app_the_entry_and_card_are_there(
        self, run_in_subprocess
    ) -> None:
        with_mfa = run_in_subprocess("tests.settings", SCRIPT)

        assert with_mfa["mfa_installed"]
        _status, page = with_mfa["account_center"]
        assert "Two-factor authentication" in page
        assert "Manage two-factor authentication" in page
        assert "passkey_login" in with_mfa["sign_in"][1]
