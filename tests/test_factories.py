"""The mirror of ``tests/factories.py``: the factories build what they claim to."""

from datetime import timedelta

from django.utils import timezone
from knox.auth import TokenAuthentication
from knox.crypto import hash_token

from tests.factories import AuthTokenFactory, UserFactory


class TestAuthTokenFactory:
    def test_it_builds_a_token_for_a_saved_user(self, auth_token) -> None:
        assert auth_token.pk
        assert auth_token.user.pk

    def test_the_instance_keeps_the_complete_value(self, auth_token) -> None:
        assert hash_token(auth_token.token) == auth_token.digest
        assert auth_token.token.startswith(auth_token.token_key)

    def test_the_value_signs_in_as_the_user_the_token_belongs_to(
        self, auth_token
    ) -> None:
        user, signed_in_with = TokenAuthentication().authenticate_credentials(
            auth_token.token.encode()
        )

        assert user == auth_token.user
        assert signed_in_with == auth_token

    def test_a_user_can_be_given(self, db) -> None:
        user = UserFactory()

        assert AuthTokenFactory(user=user).user == user

    def test_two_tokens_have_different_values(self, db) -> None:
        first, second = AuthTokenFactory.create_batch(2)

        assert first.token != second.token

    def test_a_token_expires_in_the_future_by_default(self, auth_token) -> None:
        assert auth_token.expiry > timezone.now()

    def test_an_expiry_can_be_given(self, db) -> None:
        expiry = timezone.now() - timedelta(days=2)

        token = AuthTokenFactory(expiry=expiry)
        token.refresh_from_db()

        assert token.expiry == expiry

    def test_no_expiry_can_be_given(self, db) -> None:
        token = AuthTokenFactory(expiry=None)
        token.refresh_from_db()

        assert token.expiry is None

    def test_a_created_time_can_be_given(self, db) -> None:
        created = timezone.now() - timedelta(days=10)

        token = AuthTokenFactory(created=created)
        token.refresh_from_db()

        assert token.created == created

    def test_overriding_created_leaves_the_value_working(self, db) -> None:
        token = AuthTokenFactory(created=timezone.now() - timedelta(days=10))

        user, _ = TokenAuthentication().authenticate_credentials(token.token.encode())

        assert user == token.user
