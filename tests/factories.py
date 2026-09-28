"""One factory per model the tests build."""

import os

import factory
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import TOTP, generate_totp_secret
from allauth.mfa.webauthn.internal.auth import WebAuthn
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from fido2 import cbor
from fido2.utils import websafe_encode
from fido2.webauthn import AttestedCredentialData, AuthenticatorData

from demo.models import PhoneNumber

PASSWORD = "password"


def registration_response(passkey: bool) -> dict:
    """A registration response the way a browser sends it, and fido2 parses it.

    allauth parses every stored security key before it starts an authentication
    or a registration, so the stored credential has to be well formed. The key
    is a fixed test key. ``credProps.rk`` is what tells a passkey from a
    security key.
    """
    public_key = {1: 2, 3: -7, -1: 1, -2: os.urandom(32), -3: os.urandom(32)}
    credential_id = os.urandom(16)
    credential_data = AttestedCredentialData.create(
        bytes(16), credential_id, public_key
    )
    auth_data = AuthenticatorData.create(
        bytes(32),
        AuthenticatorData.FLAG.UP | AuthenticatorData.FLAG.AT,
        0,
        credential_data,
    )
    attestation = cbor.encode({"fmt": "none", "attStmt": {}, "authData": auth_data})
    client_data = (
        b'{"type":"webauthn.create","challenge":"AAAA","origin":"http://testserver"}'
    )
    return {
        "id": websafe_encode(credential_id),
        "rawId": websafe_encode(credential_id),
        "type": "public-key",
        "response": {
            "clientDataJSON": websafe_encode(client_data),
            "attestationObject": websafe_encode(attestation),
        },
        "clientExtensionResults": {"credProps": {"rk": passkey}},
    }


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


class AuthenticatorFactory(DjangoModelFactory):
    """A second factor for a user, built through allauth's own activation.

    An authenticator app by default. The ``recovery_codes`` trait makes the
    person's recovery codes instead, and the ``webauthn`` trait a security key
    called ``key_name`` that is a passkey when ``passkey`` is set. All go through
    the calls allauth's views make, so the stored data is exactly what a real
    activation stores.
    """

    class Meta:
        model = Authenticator

    class Params:
        recovery_codes = factory.Trait(type=Authenticator.Type.RECOVERY_CODES)
        webauthn = factory.Trait(type=Authenticator.Type.WEBAUTHN)

    user = factory.SubFactory(UserFactory)
    type = Authenticator.Type.TOTP
    # Not model fields: read and removed in ``_create``.
    secret = factory.LazyFunction(generate_totp_secret)
    key_name = factory.Sequence(lambda n: f"Key {n}")
    passkey = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user, secret = kwargs["user"], kwargs.pop("secret")
        key_name, passkey = kwargs.pop("key_name"), kwargs.pop("passkey")
        if kwargs["type"] == Authenticator.Type.RECOVERY_CODES:
            return RecoveryCodes.activate(user).instance
        if kwargs["type"] == Authenticator.Type.WEBAUTHN:
            return WebAuthn.add(user, key_name, registration_response(passkey)).instance
        return TOTP.activate(user, secret).instance
