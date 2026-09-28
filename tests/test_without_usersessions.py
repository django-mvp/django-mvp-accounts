"""What this package does in a project that keeps allauth without its user sessions app.

It runs in a subprocess under ``tests/settings_without_usersessions.py``: which
apps are installed is decided when Django starts, so the running suite cannot
remove one. The subject is that startup, so the module mirrors no source file.
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
    from django.urls import NoReverseMatch, reverse

    import mvp_accounts  # noqa: F401

    call_command("migrate", verbosity=0)
    user = get_user_model().objects.create_user("person", password="password")
    client = Client()
    client.force_login(user)

    account_center = client.get(reverse("account-center"))
    overview = client.get(reverse("overview"))
    try:
        reverse("usersessions_list")
        routed = True
    except NoReverseMatch:
        routed = False

    print(json.dumps({
        "account_installed": apps.is_installed("allauth.account"),
        "usersessions_installed": apps.is_installed("allauth.usersessions"),
        "sessions_routed": routed,
        "account_email_url": reverse("account_email"),
        "account_change_password_url": reverse("account_change_password"),
        "account_center": [account_center.status_code, account_center.content.decode()],
        "overview": [overview.status_code, overview.content.decode()],
    }))
    """
)


@pytest.fixture(scope="module")
def result(run_in_subprocess) -> dict:
    return run_in_subprocess("tests.settings_without_usersessions", SCRIPT)


class TestWithoutUserSessions:
    def test_the_subprocess_really_runs_without_the_user_sessions_app(
        self, result
    ) -> None:
        assert result["account_installed"]
        assert not result["usersessions_installed"]
        assert not result["sessions_routed"]

    def test_the_account_center_renders(self, result) -> None:
        status, _page = result["account_center"]
        assert status == 200

    def test_the_account_center_still_offers_the_account_pages(self, result) -> None:
        _status, page = result["account_center"]
        assert f'href="{result["account_email_url"]}"' in page
        assert f'href="{result["account_change_password_url"]}"' in page

    def test_the_account_center_has_no_sessions_entry_or_card(self, result) -> None:
        _status, page = result["account_center"]
        assert 'href="/accounts/sessions/"' not in page

    def test_the_landing_page_renders_without_a_sessions_entry(self, result) -> None:
        status, page = result["overview"]
        assert status == 200
        assert 'href="/accounts/sessions/"' not in page
