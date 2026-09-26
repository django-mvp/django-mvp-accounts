"""What this package does in a project that keeps allauth without its social account app.

It runs in a subprocess under ``tests/settings_without_socialaccount.py``: which
apps are installed is decided when Django starts, so the running suite cannot
remove one. The subject is that startup, so the module mirrors no source file.
"""

import textwrap

import pytest

SCRIPT = textwrap.dedent(
    """
    import json
    import re

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
    overview = client.get(reverse("overview"))
    client.logout()
    sign_in = client.get(reverse("account_login"))

    print(json.dumps({
        "account_installed": apps.is_installed("allauth.account"),
        "socialaccount_installed": apps.is_installed("allauth.socialaccount"),
        "account_center": [account_center.status_code, account_center.content.decode()],
        "overview": [overview.status_code, overview.content.decode()],
        "sign_in": [sign_in.status_code, sign_in.content.decode()],
    }))
    """
)


@pytest.fixture(scope="module")
def result(run_in_subprocess) -> dict:
    """Start Django with allauth but no social account app and render the pages."""
    return run_in_subprocess("tests.settings_without_socialaccount", SCRIPT)


class TestWithoutSocialAccount:
    """A project that installs allauth's account app and not its social one."""

    def test_the_subprocess_really_runs_without_the_social_account_app(
        self, result
    ) -> None:
        assert result["account_installed"]
        assert not result["socialaccount_installed"]

    def test_the_account_center_renders(self, result) -> None:
        status, _page = result["account_center"]
        assert status == 200

    def test_the_account_center_still_offers_the_account_pages(self, result) -> None:
        _status, page = result["account_center"]
        assert "Manage email" in page
        assert "Change password" in page

    def test_the_account_center_has_no_connected_accounts_entry_or_card(
        self, result
    ) -> None:
        _status, page = result["account_center"]
        assert "Connected accounts" not in page
        assert "Manage connected accounts" not in page

    def test_the_landing_page_renders(self, result) -> None:
        status, _page = result["overview"]
        assert status == 200

    def test_the_landing_page_has_no_connected_accounts_entry(self, result) -> None:
        _status, page = result["overview"]
        assert "Connected accounts" not in page

    def test_the_sign_in_page_renders_with_no_provider_button(self, result) -> None:
        status, page = result["sign_in"]
        assert status == 200
        assert "/login/?" not in page
        assert "Or use a third-party" not in page
