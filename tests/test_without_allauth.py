"""What this package does in a project that does not install allauth.

It runs in a subprocess under ``tests/settings_without_allauth.py``: which apps
are installed is decided when Django starts, so the running suite cannot switch
allauth off. The subject is that startup, so the module mirrors no source file.
"""

import json
import os
import subprocess
import sys
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
    from mvp.menus import AccountCenterMenu

    call_command("migrate", verbosity=0)
    user = get_user_model().objects.create_user("person", password="password")
    client = Client()
    client.force_login(user)

    overview = client.get(reverse("overview"))
    account_center = client.get(reverse("account-center"))

    print(json.dumps({
        "allauth_installed": apps.is_installed("allauth.account"),
        "package_installed": apps.is_installed("mvp_accounts"),
        "menu": [child.name for child in AccountCenterMenu.children],
        "overview": [overview.status_code, overview.content.decode()],
        "account_center": [account_center.status_code, account_center.content.decode()],
    }))
    """
)


@pytest.fixture(scope="module")
def result() -> dict:
    """Start Django without allauth and report what it built and rendered."""
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-c", SCRIPT],
        capture_output=True,
        text=True,
        check=False,
        env={
            # Coverage passes its configuration to the subprocess through
            # these, so the subprocess is measured along with the suite.
            **{k: v for k, v in os.environ.items() if k.startswith("COVERAGE")},
            "DJANGO_SETTINGS_MODULE": "tests.settings_without_allauth",
            "PATH": "",
            "PYTHONPATH": ".",
        },
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


class TestWithoutAllauth:
    """A project that installs this package but not allauth."""

    def test_the_subprocess_really_runs_without_allauth(self, result) -> None:
        assert result["package_installed"]
        assert not result["allauth_installed"]

    def test_the_menu_holds_none_of_this_packages_entries(self, result) -> None:
        assert not {"email", "password", "phone"} & set(result["menu"])

    def test_the_demo_overview_renders(self, result) -> None:
        status, _page = result["overview"]
        assert status == 200

    def test_the_account_center_renders_without_this_packages_cards(
        self, result
    ) -> None:
        status, page = result["account_center"]
        assert status == 200
        assert "Change password" not in page
        assert "Manage email" not in page
        assert "Change phone number" not in page
