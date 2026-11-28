"""Tests for the browser-test machinery in ``tests/conftest.py``.

Getting it wrong is invisible. A guard that skips in CI turns every browser test
into a green skip, and a page that reaches the network passes on a machine that
is online and fails on one that is not.
"""

import re

import pytest

from tests import conftest
from tests.conftest import (
    OFF_THIS_MACHINE,
    RequestsInFlight,
    _should_skip_browser_tests,
    answer_request,
)


class TestShouldSkipBrowserTests:
    def test_a_missing_browser_skips_locally_and_fails_in_ci(self):
        assert _should_skip_browser_tests(has_browser=False, env={}) is True
        assert (
            _should_skip_browser_tests(has_browser=False, env={"CI": "true"}) is False
        )


class FakeRoute:
    """The answers a Playwright route can give, recorded."""

    def __init__(self):
        self.answer = None
        self.body = None

    def abort(self, reason):
        self.answer = "abort"

    def fulfill(self, body, content_type, headers):
        self.answer = "fulfill"
        self.body = body


class FakeRequest:
    def __init__(self, url, method="GET"):
        self.url = url
        self.method = method


def _answer(url):
    route, external = FakeRoute(), []
    answer_request(route, FakeRequest(url), external)
    return route, external


class TestAnswerRequest:
    def test_a_request_to_any_other_host_is_refused_and_recorded(self):
        route, external = _answer("https://example.com/tracker.js")

        assert route.answer == "abort"
        assert external == ["GET https://example.com/tracker.js"]

    def test_a_request_with_a_stand_in_is_answered_from_it(self, monkeypatch):
        stand_in = (re.compile(r"https://cdn\.example/lib\.js"), b"// lib", "text/js")
        monkeypatch.setattr(conftest, "STAND_INS", (stand_in,))

        route, external = _answer("https://cdn.example/lib.js")

        assert (route.answer, route.body, external) == ("fulfill", b"// lib", [])


class TestOffThisMachine:
    def test_only_addresses_on_other_machines_match(self):
        addresses = {
            "http://localhost:8123/accounts/": False,
            "http://127.0.0.1:41233/": False,
            "http://[::1]:8000/x": False,
            "https://example.com/localhost/": True,
            "http://localhost.example.com/": True,
        }

        matched = {url: bool(OFF_THIS_MACHINE.match(url)) for url in addresses}

        assert matched == addresses


class TestRequestsInFlight:
    def test_the_count_returns_to_zero_when_every_request_has_finished(self):
        counter = RequestsInFlight()

        counter._started()
        counter._started()
        counter._finished()
        assert counter._count == 1

        counter._finished()
        counter.wait_until_idle()

    def test_a_request_that_began_before_watching_does_not_make_the_count_negative(
        self,
    ):
        counter = RequestsInFlight()

        counter._finished()

        assert counter._count == 0

    def test_waiting_for_idle_fails_while_a_request_is_unanswered(self, monkeypatch):
        counter = RequestsInFlight()
        counter._started()
        monkeypatch.setattr(conftest, "wait_until", _wait_without_sleeping)

        with pytest.raises(AssertionError, match="never reached"):
            counter.wait_until_idle()


def _wait_without_sleeping(condition, timeout=5.0, interval=0.02):
    """``wait_until`` with its deadline already passed, so a test need not wait."""
    assert condition(), "the state was never reached"
