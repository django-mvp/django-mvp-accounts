"""What this package does without django-rest-knox or Django REST framework.

It runs in a subprocess under ``tests/settings_without_knox.py``: whether a
package can be imported is decided when Django starts, so the running suite,
which has both, cannot show their absence. Both are made unimportable before
Django starts, which is what an uninstalled package looks like. The subject is
that startup, so the module mirrors no source file.
"""

import textwrap

import pytest

TOKENS_PATH = "/account/tokens/"

SCRIPT = textwrap.dedent(
    """
    import json
    import sys

    sys.modules["knox"] = None
    sys.modules["rest_framework"] = None

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

    overview = client.get(reverse("overview"))
    account_center = client.get(reverse("account-center"))

    try:
        reverse("account_api_tokens")
        routed = True
    except NoReverseMatch:
        routed = False

    print(json.dumps({
        "knox_installed": apps.is_installed("knox"),
        "rest_framework_installed": apps.is_installed("rest_framework"),
        "package_installed": apps.is_installed("mvp_accounts"),
        "tokens_routed": routed,
        "overview": [overview.status_code, overview.content.decode()],
        "account_center": [account_center.status_code, account_center.content.decode()],
        "imported": sorted(
            name
            for name, module in sys.modules.items()
            if module is not None
            and name.split(".")[0] in {"knox", "rest_framework"}
        ),
    }))
    """
)


@pytest.fixture(scope="module")
def result(run_in_subprocess) -> dict:
    return run_in_subprocess("tests.settings_without_knox", SCRIPT)


class TestWithoutKnox:
    def test_the_subprocess_really_runs_without_either_package(self, result) -> None:
        assert result["package_installed"]
        assert not result["knox_installed"]
        assert not result["rest_framework_installed"]
        assert not result["tokens_routed"]

    def test_neither_package_was_imported(self, result) -> None:
        assert result["imported"] == []

    def test_the_landing_page_renders(self, result) -> None:
        status, _page = result["overview"]
        assert status == 200

    def test_the_account_center_renders(self, result) -> None:
        status, _page = result["account_center"]
        assert status == 200

    def test_the_account_center_has_no_tokens_entry_or_card(self, result) -> None:
        _status, page = result["account_center"]
        assert f'href="{TOKENS_PATH}"' not in page
