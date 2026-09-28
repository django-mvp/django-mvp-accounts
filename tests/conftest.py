"""Shared fixtures for the test suite.

General setup and anything reused across modules lives here. Test modules hold
assertions, not construction boilerplate.

Once this package has models, each one gets exactly one ``factory_boy``
factory in ``tests/factories.py``, and the fixtures here are thin wrappers over
those factories. A one-off variation needs no fixture of its own — call the
factory inline in the test with the field overridden.
"""

import importlib
import json
import os
import subprocess
import sys
from contextlib import contextmanager

import pytest
from allauth.mfa.totp.internal.auth import (
    format_hotp_value,
    hotp_value,
    yield_hotp_counters_from_time,
)
from bs4 import BeautifulSoup
from django import template as dj_template
from django.template import Context
from django.test import override_settings
from django.urls import clear_url_caches, reverse
from django_cotton.compiler_regex import CottonCompiler

from tests.factories import EmailAddressFactory


@pytest.fixture(scope="session")
def render():
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def totp_code():
    def code_for(secret: str) -> str:
        counter = next(yield_hotp_counters_from_time())
        return format_hotp_value(hotp_value(secret, counter))

    return code_for


@pytest.fixture
def signed_in_client(client, db):
    address = EmailAddressFactory()
    client.force_login(address.user)
    client.user = address.user
    return client


@pytest.fixture
def assert_script_hooks():
    def check(html: str) -> int:
        soup = BeautifulSoup(html, "html.parser")
        hooks = soup.select("script[data-allauth-onload]")
        for hook in hooks:
            for name, element_id in json.loads(hook.string)["ids"].items():
                assert soup.find(id=element_id), (
                    f"{hook['data-allauth-onload']} needs #{element_id} ({name})"
                )
        return len(hooks)

    return check


# The views come first: a view class reads some settings, the template it
# renders among them, when it is defined, and the URLconf holds the classes.
URLCONF_MODULES = (
    "allauth.account.views",
    "allauth.account.urls",
    "allauth.mfa.base.urls",
    "allauth.mfa.webauthn.urls",
    "allauth.mfa.urls",
    "allauth.urls",
    "demo.urls",
    "tests.urls",
)


def reload_urlconf():
    """Import the views and routes again, so they follow the settings as they stand."""
    for name in URLCONF_MODULES:
        importlib.reload(importlib.import_module(name))
    clear_url_caches()


@pytest.fixture
def rebuild_urls():
    @contextmanager
    def rebuild(**overrides):
        try:
            with override_settings(**overrides):
                reload_urlconf()
                yield
        finally:
            reload_urlconf()

    return rebuild


@pytest.fixture(scope="session")
def run_in_subprocess():
    def run(settings_module: str, script: str) -> dict:
        completed = subprocess.run(  # noqa: S603
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=False,
            env={
                # Coverage passes its configuration to the subprocess through
                # these, so the subprocess is measured along with the suite.
                **{k: v for k, v in os.environ.items() if k.startswith("COVERAGE")},
                "DJANGO_SETTINGS_MODULE": settings_module,
                "PATH": "",
                "PYTHONPATH": ".",
            },
            timeout=120,
        )
        assert completed.returncode == 0, completed.stderr
        return json.loads(completed.stdout.strip().splitlines()[-1])

    return run
