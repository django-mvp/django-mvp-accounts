"""Shared fixtures for the test suite.

General setup and anything reused across modules lives here. Test modules hold
assertions, not construction boilerplate.

Once this package has models, each one gets exactly one ``factory_boy``
factory in ``tests/factories.py``, and the fixtures here are thin wrappers over
those factories. A one-off variation needs no fixture of its own — call the
factory inline in the test with the field overridden.
"""

import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
from allauth.mfa.totp.internal.auth import (
    format_hotp_value,
    hotp_value,
    yield_hotp_counters_from_time,
)
from bs4 import BeautifulSoup
from django import template as dj_template
from django.core.signals import request_finished, request_started
from django.template import Context
from django.test import override_settings
from django.urls import clear_url_caches, reverse
from django_cotton.compiler_regex import CottonCompiler

from tests.factories import PASSWORD, AuthTokenFactory, EmailAddressFactory


@pytest.fixture(scope="session")
def render():
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def totp_code():
    def code_for(secret: str) -> str:
        counter = next(yield_hotp_counters_from_time())
        return format_hotp_value(hotp_value(secret, counter))

    return code_for


@pytest.fixture
def signed_in_client(client, db):
    address = EmailAddressFactory()
    client.force_login(address.user)
    client.user = address.user
    return client


@pytest.fixture
def sign_in(db, settings):
    """Sign a person in through allauth's sign-in form.

    ``force_login`` records no sign-in, so a page that asks a person who has not
    signed in recently to confirm who they are, such as creating an API token,
    needs a person signed in this way. allauth's sign-in rate limit is off,
    because the suite signs in from one address far more often than it allows,
    and the page it lands on is opened here, which shows and clears the
    "signed in" message so no test sees it.
    """
    settings.ACCOUNT_RATE_LIMITS = False

    def sign_in(client, address=None):
        address = address or EmailAddressFactory()
        response = client.post(
            reverse("account_login"), {"login": address.email, "password": PASSWORD}
        )
        assert response.status_code == 302
        client.get(response["Location"])
        client.user = address.user
        return client

    return sign_in


@pytest.fixture
def auth_token(db):
    return AuthTokenFactory()


@pytest.fixture
def assert_script_hooks():
    def check(html: str) -> int:
        soup = BeautifulSoup(html, "html.parser")
        hooks = soup.select("script[data-allauth-onload]")
        for hook in hooks:
            for name, element_id in json.loads(hook.string)["ids"].items():
                assert soup.find(id=element_id), (
                    f"{hook['data-allauth-onload']} needs #{element_id} ({name})"
                )
        return len(hooks)

    return check


# The views come first: a view class reads some settings, the template it
# renders among them, when it is defined, and the URLconf holds the classes.
URLCONF_MODULES = (
    "allauth.account.views",
    "allauth.account.urls",
    "allauth.mfa.base.urls",
    "allauth.mfa.webauthn.urls",
    "allauth.mfa.urls",
    "allauth.urls",
    "demo.urls",
    "tests.urls",
)


def reload_urlconf():
    """Import the views and routes again, so they follow the settings as they stand."""
    for name in URLCONF_MODULES:
        importlib.reload(importlib.import_module(name))
    clear_url_caches()


@pytest.fixture
def rebuild_urls():
    @contextmanager
    def rebuild(**overrides):
        try:
            with override_settings(**overrides):
                reload_urlconf()
                yield
        finally:
            reload_urlconf()

    return rebuild


@pytest.fixture(scope="session")
def run_in_subprocess():
    def run(settings_module: str, script: str) -> dict:
        completed = subprocess.run(  # noqa: S603
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=False,
            env={
                # Coverage passes its configuration to the subprocess through
                # these, so the subprocess is measured along with the suite.
                **{k: v for k, v in os.environ.items() if k.startswith("COVERAGE")},
                "DJANGO_SETTINGS_MODULE": settings_module,
                "PATH": "",
                "PYTHONPATH": ".",
            },
            timeout=120,
        )
        assert completed.returncode == 0, completed.stderr
        return json.loads(completed.stdout.strip().splitlines()[-1])

    return run


# Browser tests -------------------------------------------------------------------

#: How long a browser action, a navigation or an ``expect`` waits. A short wait
#: fails now and then on a loaded CI runner.
BROWSER_TIMEOUT_MS = 20_000

VENDORED = Path(__file__).resolve().parent / "fixtures" / "vendor"

_ICONS = r"https://cdn\.jsdelivr\.net/npm/bootstrap-icons@1\.13\.1/font/"

#: What the browser tests serve in place of the hosts a page asks for, so no
#: browser test needs the network: ``(address pattern, answer, content type)``.
#: The pattern matches the whole URL. The answer is the bytes to send, or a
#: function from the match to the file to send. The files under
#: ``tests/fixtures/vendor`` are copies of the published releases.
STAND_INS = (
    (
        re.compile(_ICONS + r"bootstrap-icons\.min\.css"),
        lambda match: VENDORED / "bootstrap-icons.min.css",
        "text/css",
    ),
    (
        re.compile(_ICONS + r"fonts/bootstrap-icons\.woff2(?:\?.*)?"),
        lambda match: VENDORED / "bootstrap-icons.woff2",
        "font/woff2",
    ),
)

#: Every web address that is not on this machine. Only these go through Python:
#: a test that waits with ``wait_until`` does not run Playwright, so a request
#: held for Python's answer would stall until the test's next browser call.
OFF_THIS_MACHINE = re.compile(
    r"^https?://(?!(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?(?:/|$))"
)

#: Tests that take over a second or start a subprocess, by node id prefix. The
#: quick selection ``-m "not e2e and not slow"`` skips them. Browser tests carry
#: ``e2e`` instead, so they are not listed here.
SLOW_TESTS: tuple[str, ...] = (
    "tests/test_demo.py::TestDemoSignIn::",
    "tests/test_demo.py::TestDemoTokenAccess::",
    "tests/test_demo.py::TestDemoTwoFactorAccount::",
    "tests/test_demo.py::TestSeededApiTokens::",
    "tests/test_demo.py::TestSeededSessions::",
    "tests/test_demo.py::TestSeededSessionsWalkthrough::",
    "tests/test_demo.py::TestSeededSocialAccounts::",
    "tests/test_demo.py::TestSeededStates::",
    "tests/test_two_factor_sign_in.py::TestActivateThenSignIn::",
    # These start Django in a subprocess, because allauth, knox and the rest
    # cannot be uninstalled from a running one.
    "tests/test_without_",
)


def _browser_is_installed():
    """True when Playwright is importable *and* its browser is downloaded.

    Testing the import alone is not enough. Installing the package is one
    step and downloading the browser is another, so a CI runner that has the
    dependency but has never run ``playwright install`` errors at launch
    instead of skipping.
    """
    if importlib.util.find_spec("playwright") is None:
        return False

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            return Path(p.chromium.executable_path).exists()
    except Exception:
        return False


def _should_skip_browser_tests(has_browser, env):
    """Decide whether browser-marked tests skip, given the browser and the environment.

    Locally a missing browser is ordinary: a contributor who has not run
    ``playwright install`` should see skips, not a wall of errors.

    In CI it is a failure. The workflow installs a browser, so one is always
    expected there, and skipping would hide exactly what this guard exists to
    surface: every browser test skipped reads as every browser test passed.
    """
    if has_browser:
        return False
    return env.get("CI", "").lower() not in {"1", "true"}


HAS_BROWSER = _browser_is_installed()

requires_browser = pytest.mark.skipif(
    _should_skip_browser_tests(HAS_BROWSER, os.environ),
    reason="playwright browser not installed (run: playwright install chromium)",
)


def wait_for_alpine(page):
    """Wait until Alpine has started and initialised every ``x-data`` element.

    Args:
        page: The Playwright page.

    ``window.Alpine`` exists as soon as the script has run, but a handler is not
    wired until Alpine initialises its element. A click before that does nothing.
    """
    page.wait_for_function(
        "() => window.Alpine && Alpine.version"
        " && [...document.querySelectorAll('[x-data]')].every(el => el._x_dataStack)"
    )


def wait_until_still(page):
    """Wait until nothing on the page is being requested or moving.

    No htmx request is in flight, no swap is settling and no CSS transition is
    running, for two animation frames in a row. This is the state a fixed pause
    after a gesture would stand in for.

    Args:
        page: The Playwright page.

    Raises:
        AssertionError: If the page is still busy after about 600 frames.
    """
    still = page.evaluate(
        """async () => {
          const frame = () => new Promise(done => requestAnimationFrame(done));
          const busy = () => document.querySelector(
            '.htmx-request, .htmx-swapping, .htmx-settling, .htmx-added'
          ) || document.getAnimations().some(a => a instanceof CSSTransition);
          let quiet = 0;
          for (let tries = 0; tries < 600 && quiet < 2; tries++) {
            await frame();
            quiet = busy() ? 0 : quiet + 1;
          }
          return quiet >= 2;
        }"""
    )
    assert still, "the page never came to rest"


def wait_until(condition, timeout=5.0, interval=0.02):
    """Poll ``condition`` until it is true, for state on the server side.

    A browser event, such as a dialog, reaches the test only during a Playwright
    call, so this never sees one. Wait for those with ``page.expect_event``.

    Args:
        condition: A callable returning a truthy value once the state is reached.
        timeout: Seconds to wait before failing.
        interval: Seconds between looks.
    """
    deadline = time.monotonic() + timeout
    while not condition():
        assert time.monotonic() < deadline, "the state was never reached"
        time.sleep(interval)


def pytest_collection_modifyitems(config, items):
    """Mark every browser test ``e2e`` and the listed slow tests ``slow``.

    A test is a browser test when its fixtures reach Playwright's ``browser``.
    Marking here means a new browser test cannot miss the marker, and
    ``pytest -m "not e2e and not slow"`` is the whole suite without them.
    """
    for item in items:
        if "browser" in item.fixturenames:
            item.add_marker(pytest.mark.e2e)
        if item.nodeid.startswith(SLOW_TESTS):
            item.add_marker(pytest.mark.slow)


def answer_request(route, request, external):
    """Answer one request a browser context makes.

    Only requests to other machines reach this function (see ``OFF_THIS_MACHINE``).
    One to an address in ``STAND_INS`` is answered from the repository. Any other
    is refused and recorded in ``external``, which fails the test when it ends,
    so a page cannot reach the network without a test noticing.

    Args:
        route: The Playwright route for the request.
        request: The Playwright request.
        external: A list that collects ``"METHOD url"`` for each refused request.
    """
    url = request.url
    for pattern, answer, content_type in STAND_INS:
        match = pattern.fullmatch(url)
        if match:
            try:
                body = answer(match).read_bytes() if callable(answer) else answer
            except OSError as error:
                # An unanswered route hangs the page until its timeout and hides why.
                external.append(
                    f"{request.method} {url} (stand-in unreadable: {error})"
                )
                route.abort("failed")
                return
            route.fulfill(
                body=body,
                content_type=content_type,
                headers={"access-control-allow-origin": "*"},
            )
            return
    external.append(f"{request.method} {url}")
    route.abort("blockedbyclient")


def _configure_context(context, external):
    """Apply the suite's timeouts to a browser context and keep it off the network.

    Args:
        context: The Playwright browser context.
        external: The list that ``answer_request`` records refused requests in.
    """
    context.set_default_timeout(BROWSER_TIMEOUT_MS)
    context.set_default_navigation_timeout(BROWSER_TIMEOUT_MS)
    # Routing turns the browser's HTTP cache off for the context.
    context.route(
        OFF_THIS_MACHINE,
        lambda route, request: answer_request(route, request, external),
    )


class RequestsInFlight:
    """Count the requests the live server is answering at this moment.

    The live server answers in threads of its own, and the settings are shared
    with the test. A value put back while a request is still being answered is
    read half-way, and the next test inherits the last one's page. Waiting for
    this count to reach zero is what puts it back between requests.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._count = 0

    def _started(self, **kwargs):
        with self._lock:
            self._count += 1

    def _finished(self, **kwargs):
        with self._lock:
            # A request that began before ``watch`` still finishes after it.
            self._count = max(0, self._count - 1)

    def watch(self):
        """Start counting."""
        request_started.connect(self._started, weak=False)
        request_finished.connect(self._finished, weak=False)

    def stop(self):
        """Stop counting."""
        request_started.disconnect(self._started)
        request_finished.disconnect(self._finished)

    def wait_until_idle(self):
        """Wait until the live server has finished every request it was sent."""
        wait_until(lambda: self._count == 0, timeout=15)


@pytest.fixture
def requests_in_flight():
    """The live server's request count, and an idle server before the test ends.

    A browser test's pages are closed before this fixture ends, and the test's
    ``monkeypatch`` undoes after it, so a value the test set with
    ``monkeypatch.setattr`` is put back only once no request can still be
    reading it. Settings changed through the ``settings`` fixture are put back
    earlier and are not covered.
    """
    counter = RequestsInFlight()
    counter.watch()
    yield counter
    try:
        counter.wait_until_idle()
    finally:
        counter.stop()


@pytest.fixture(autouse=True)
def _browser_defaults(request, monkeypatch):
    """Give every browser context a timeout that survives a loaded runner, keep
    it off the network, and fail the test that reached out to it.

    The contexts a test opens itself through ``browser.new_context`` or
    ``browser.new_page`` are configured the same way as the ``page`` fixture's.
    This fixture is set up before the others a test asks for, so it ends after
    them: the pages are closed by the time it checks.
    """
    if "browser" not in request.fixturenames:
        yield
        return
    from playwright.sync_api import expect

    expect.set_options(timeout=BROWSER_TIMEOUT_MS)
    external = []
    request.getfixturevalue("requests_in_flight")
    browser = request.getfixturevalue("browser")
    new_context, new_page = browser.new_context, browser.new_page

    def configured_context(*args, **kwargs):
        context = new_context(*args, **kwargs)
        _configure_context(context, external)
        return context

    def configured_page(*args, **kwargs):
        page = new_page(*args, **kwargs)
        _configure_context(page.context, external)
        return page

    monkeypatch.setattr(browser, "new_context", configured_context)
    monkeypatch.setattr(browser, "new_page", configured_page)
    yield
    assert not external, (
        "the browser test reached the network. Vendor what the page asks for "
        "(see STAND_INS in tests/conftest.py): " + ", ".join(external)
    )
