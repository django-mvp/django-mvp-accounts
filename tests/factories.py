"""One factory per model the tests build."""

import factory
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
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
