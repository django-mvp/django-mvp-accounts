"""What this package does in a project that does not install allauth.

It runs in a subprocess under ``tests/settings_without_allauth.py``: which apps
are installed is decided when Django starts, so the running suite cannot switch
allauth off. The subject is that startup, so the module mirrors no source file.
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
    from mvp.menus import AccountCenterMenu

    call_command("migrate", verbosity=0)
    user = get_user_model().objects.create_user("person", password="password")
    client = Client()
    client.force_login(user)

    overview = client.get(reverse("overview"))
    account_center = client.get(reverse("account-center"))
    tokens_url = reverse("account_api_tokens")
    tokens_page = client.get(tokens_url)
    group = AccountCenterMenu.get("account")

    print(json.dumps({
        "allauth_installed": apps.is_installed("allauth.account"),
        "package_installed": apps.is_installed("mvp_accounts"),
        "menu": [child.name for child in AccountCenterMenu.children],
        "account_entries": [child.name for child in group.children],
        "tokens_url": tokens_url,
        "tokens_page": tokens_page.status_code,
        "overview": [overview.status_code, overview.content.decode()],
        "account_center": [account_center.status_code, account_center.content.decode()],
    }))
    """
)


@pytest.fixture(scope="module")
def result(run_in_subprocess) -> dict:
    return run_in_subprocess("tests.settings_without_allauth", SCRIPT)


class TestWithoutAllauth:
    def test_the_subprocess_really_runs_without_allauth(self, result) -> None:
        assert result["package_installed"]
        assert not result["allauth_installed"]

    def test_the_account_group_holds_only_the_api_tokens_entry(self, result) -> None:
        assert "account" in result["menu"]
        assert result["account_entries"] == ["api_tokens"]

    def test_the_demo_overview_renders(self, result) -> None:
        status, _page = result["overview"]
        assert status == 200

    def test_the_account_center_renders_without_this_packages_cards(
        self, result
    ) -> None:
        status, page = result["account_center"]
        assert status == 200
        assert 'href="/accounts/password/change/"' not in page
        assert 'href="/accounts/email/"' not in page
        assert 'href="/accounts/phone/change/"' not in page

    def test_the_account_center_has_the_api_tokens_entry(self, result) -> None:
        _status, page = result["account_center"]
        assert f'href="{result["tokens_url"]}"' in page

    def test_the_tokens_page_answers_a_signed_in_person(self, result) -> None:
        assert result["tokens_page"] == 200
