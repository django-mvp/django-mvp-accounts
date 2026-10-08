"""The mirror of ``mvp_accounts/templatetags/mvp_accounts.py``."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import RequestFactory

from tests.factories import UserFactory

SOURCE = "{% load mvp_accounts %}{% may_use_api_tokens as allowed %}{{ allowed }}"


def render(**context) -> str:
    return Template(SOURCE).render(Context(context))


def request_of(user) -> object:
    request = RequestFactory().get("/")
    request.user = user
    return request


class TestMayUseApiTokens:
    def test_it_is_true_for_a_signed_in_person_when_no_setting_names_a_function(
        self, db
    ) -> None:
        assert render(request=request_of(UserFactory())) == "True"

    def test_it_is_false_for_a_visitor(self) -> None:
        assert render(request=request_of(AnonymousUser())) == "False"

    @pytest.mark.parametrize(
        ("is_staff", "expected"), [(True, "True"), (False, "False")]
    )
    def test_it_gives_the_projects_answer_for_the_requests_user(
        self, db, settings, is_staff, expected
    ) -> None:
        settings.MVP_ACCOUNTS_API_TOKEN_ACCESS = "tests.access.staff_only"

        assert render(request=request_of(UserFactory(is_staff=is_staff))) == expected

    def test_it_is_false_without_a_request(self) -> None:
        assert render() == "False"
