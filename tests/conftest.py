"""Shared fixtures for the test suite.

General setup and anything reused across modules lives here. Test modules hold
assertions, not construction boilerplate.

Once this package has models, each one gets exactly one ``factory_boy``
factory in ``tests/factories.py``, and the fixtures here are thin wrappers over
those factories. A one-off variation needs no fixture of its own — call the
factory inline in the test with the field overridden.
"""

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
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
