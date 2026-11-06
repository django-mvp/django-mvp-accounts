"""Fixtures shared by the tokens page tests."""

import pytest

from tests.factories import EmailAddressFactory


@pytest.fixture
def signed_in_client(client, sign_in):
    """A person who has just signed in, so creating a token asks nothing more."""
    return sign_in(client)


@pytest.fixture
def stale_client(client, db):
    """A signed-in person whose sign-in allauth has no record of."""
    address = EmailAddressFactory()
    client.force_login(address.user)
    client.user = address.user
    return client
