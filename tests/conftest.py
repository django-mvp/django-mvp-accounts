"""Shared fixtures for the test suite.

General setup and anything reused across modules lives here. Test modules hold
assertions, not construction boilerplate.

Once this package has models, each one gets exactly one ``factory_boy``
factory in ``tests/factories.py``, and the fixtures here are thin wrappers over
those factories. A one-off variation needs no fixture of its own — call the
factory inline in the test with the field overridden.
"""

import importlib
from contextlib import contextmanager

import pytest
from django import template as dj_template
from django.template import Context
from django.test import override_settings
from django.urls import clear_url_caches, reverse
from django_cotton.compiler_regex import CottonCompiler

from tests.factories import EmailAddressFactory


@pytest.fixture(scope="session")
def render():
    """Compile a Cotton source string and render it.

    No request is involved. A component that reads nothing off one renders
    anywhere a template does, including a page assembled outside the request
    cycle, and this fixture is what holds it to that.
    """
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    """The demo project's overview page, rendered, as a string."""
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def signed_in_client(client, db):
    """A test client signed in as an account with a verified primary address."""
    address = EmailAddressFactory()
    client.force_login(address.user)
    client.user = address.user
    return client


URLCONF_MODULES = ("allauth.account.urls", "allauth.urls", "demo.urls", "tests.urls")


def reload_urlconf():
    """Import the routes again, so they follow the settings as they now stand."""
    for name in URLCONF_MODULES:
        importlib.reload(importlib.import_module(name))
    clear_url_caches()


@pytest.fixture
def rebuild_urls():
    """Apply settings overrides and rebuild allauth's routes to match.

    allauth decides which account routes exist when its URLconf is imported, so
    switching a setting with ``override_settings`` alone changes nothing a test
    can see. Used as ``with rebuild_urls(ACCOUNT_LOGIN_BY_CODE_ENABLED=False):``.
    The routes are rebuilt again on the way out, from the restored settings.
    Every xdist worker is its own process, so a rebuild in one cannot reach
    another.
    """

    @contextmanager
    def rebuild(**overrides):
        try:
            with override_settings(**overrides):
                reload_urlconf()
                yield
        finally:
            reload_urlconf()

    return rebuild
