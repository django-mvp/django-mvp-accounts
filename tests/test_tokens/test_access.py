"""The mirror of ``mvp_accounts/tokens/access.py``: who may hold tokens."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings

from mvp_accounts.tokens.access import may_use_tokens
from tests import access
from tests.factories import UserFactory

STAFF_ONLY = "tests.access.staff_only"


@pytest.fixture(autouse=True)
def nobody_asked():
    access.asked.clear()


class TestMayUseTokens:
    def test_a_signed_in_person_may_when_no_setting_names_a_function(self, db) -> None:
        assert may_use_tokens(UserFactory()) is True

    def test_a_setting_of_none_is_the_same_as_none_set(self, db) -> None:
        with override_settings(MVP_ACCOUNTS_API_TOKEN_ACCESS=None):
            assert may_use_tokens(UserFactory()) is True

    def test_an_anonymous_visitor_may_not(self) -> None:
        assert may_use_tokens(AnonymousUser()) is False

    @override_settings(MVP_ACCOUNTS_API_TOKEN_ACCESS=STAFF_ONLY)
    def test_the_function_the_setting_names_decides(self, db) -> None:
        assert may_use_tokens(UserFactory(is_staff=True)) is True
        assert may_use_tokens(UserFactory(is_staff=False)) is False

    @override_settings(MVP_ACCOUNTS_API_TOKEN_ACCESS=STAFF_ONLY)
    def test_the_function_is_not_asked_about_an_anonymous_visitor(self) -> None:
        assert may_use_tokens(AnonymousUser()) is False
        assert access.asked == []

    @override_settings(MVP_ACCOUNTS_API_TOKEN_ACCESS="tests.access.returns_none")
    def test_the_answer_is_always_a_bool(self, db) -> None:
        assert may_use_tokens(UserFactory()) is False

    @override_settings(MVP_ACCOUNTS_API_TOKEN_ACCESS="tests.access.no_such_function")
    def test_a_path_that_does_not_import_raises(self, db) -> None:
        with pytest.raises(ImportError):
            may_use_tokens(UserFactory())
