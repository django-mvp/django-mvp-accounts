"""One factory per model the tests build."""

from importlib import import_module

import factory
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.usersessions.models import UserSession
from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)
from factory.django import DjangoModelFactory

from demo.models import PhoneNumber

PASSWORD = "password"


class UserFactory(DjangoModelFactory):
    """An ordinary account whose password is ``password``, like the demo's."""

    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"person{n}@example.com")
    email = factory.LazyAttribute(lambda user: user.username)
    password = factory.PostGenerationMethodCall("set_password", PASSWORD)


class EmailAddressFactory(DjangoModelFactory):
    """A verified, primary address for a user, which is what sign-in needs."""

    class Meta:
        model = EmailAddress

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda address: address.user.email)
    verified = True
    primary = True


class PhoneNumberFactory(DjangoModelFactory):
    """A verified phone number for a user."""

    class Meta:
        model = PhoneNumber

    user = factory.SubFactory(UserFactory)
    number = factory.Sequence(lambda n: f"+4915100{n:06d}")
    verified = True


class SocialAccountFactory(DjangoModelFactory):
    """An account connected through allauth's test provider."""

    class Meta:
        model = SocialAccount

    user = factory.SubFactory(UserFactory)
    provider = "dummy"
    uid = factory.Sequence(lambda n: str(5000 + n))


class UserSessionFactory(DjangoModelFactory):
    """A signed-in session for a user that no test client holds.

    Its ``session_key`` is a saved Django session carrying the user's id,
    backend and auth hash, which is what allauth needs to keep the row when it
    lists a user's sessions. A client that signs in gets its row from allauth's
    middleware on its first request, so never build one for a client's key.
    """

    class Meta:
        model = UserSession

    user = factory.SubFactory(UserFactory)
    ip = "192.0.2.1"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0"
    session_key = factory.LazyAttribute(
        lambda row: UserSessionFactory.save_django_session(row.user)
    )

    @staticmethod
    def save_django_session(user) -> str:
        """Save a Django session signed in as ``user`` and return its key."""
        store = import_module(settings.SESSION_ENGINE).SessionStore()
        store[SESSION_KEY] = user._meta.pk.value_to_string(user)
        store[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        store[HASH_SESSION_KEY] = user.get_session_auth_hash()
        store.save()
        return store.session_key
