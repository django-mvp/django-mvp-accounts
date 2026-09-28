"""allauth's sessions page renders inside django-mvp's Account Center.

The page has no template of this package's: it extends the layout every
account management page shares, and draws its table through allauth's table
elements. The suite runs under the demo's settings, so allauth's middleware is
on and a signed-in client's own row is written on its first request. The
subject is those templates, so this module does not mirror a source file.
"""

import copy
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from django.test import Client, override_settings
from django.urls import reverse

from tests.factories import UserFactory, UserSessionFactory
from tests.test_management_pages import ManagementPageAssertions

FIREFOX = "Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0"
SAFARI = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0) Safari/604.1"
CHROME = "Mozilla/5.0 (Windows NT 10.0) Chrome/129.0"


def browser(user, ip: str, user_agent: str) -> Client:
    """A client of its own, signed in as ``user`` and known to allauth.

    The row allauth records for it is written by its middleware on the first
    request, from this client's address and browser.
    """
    client = Client(REMOTE_ADDR=ip, HTTP_USER_AGENT=user_agent)
    client.force_login(user)
    client.get(reverse("overview"))
    return client


def rows_of(response) -> list[list[str]]:
    """The cells of each body row on the page, as text."""
    soup = BeautifulSoup(response.content.decode(), "html.parser")
    return [
        [td.get_text(" ", strip=True) for td in tr.select("td")]
        for tr in soup.select("tbody tr")
    ]


@pytest.fixture
def person(db):
    return UserFactory()


@pytest.fixture
def three_browsers(person) -> list[Client]:
    return [
        browser(person, "192.0.2.10", FIREFOX),
        browser(person, "198.51.100.24", SAFARI),
        browser(person, "203.0.113.7", CHROME),
    ]


class TestSessionsPage(ManagementPageAssertions):
    def test_it_is_a_management_page(self, three_browsers) -> None:
        response = three_browsers[0].get(reverse("usersessions_list"))

        self.assert_management_page(response, "<h1")

    def test_every_session_is_listed_with_its_address_and_browser(
        self, three_browsers
    ) -> None:
        rows = rows_of(three_browsers[1].get(reverse("usersessions_list")))

        assert len(rows) == 3
        listed = {(row[1], row[2]) for row in rows}
        assert listed == {
            ("192.0.2.10", FIREFOX),
            ("198.51.100.24", SAFARI),
            ("203.0.113.7", CHROME),
        }

    def test_only_the_asking_browsers_row_is_current(self, three_browsers) -> None:
        response = three_browsers[1].get(reverse("usersessions_list"))

        rows = rows_of(response)
        current = [row for row in rows if "Current" in row[-1]]
        assert len(current) == 1
        assert current[0][1] == "198.51.100.24"
        assert response.content.decode().count("Current") == 1

    def test_the_last_seen_column_shows_with_activity_tracking(
        self, three_browsers
    ) -> None:
        response = three_browsers[0].get(reverse("usersessions_list"))

        assert all(len(row) == 5 for row in rows_of(response))

    @override_settings(USERSESSIONS_TRACK_ACTIVITY=False)
    def test_the_last_seen_column_is_absent_without_activity_tracking(
        self, person
    ) -> None:
        # With tracking off allauth's middleware writes nothing, so the row is
        # the one the sign-in itself recorded.
        client = Client(REMOTE_ADDR="192.0.2.10", HTTP_USER_AGENT=FIREFOX)
        assert (
            client.post(
                reverse("account_login"),
                {"login": person.email, "password": "password"},
            ).status_code
            == 302
        )

        response = client.get(reverse("usersessions_list"))

        assert all(len(row) == 4 for row in rows_of(response))

    def test_the_table_is_a_theme_table(self, three_browsers) -> None:
        soup = BeautifulSoup(
            three_browsers[0].get(reverse("usersessions_list")).content.decode(),
            "html.parser",
        )

        table = soup.find("table")
        assert "table" in table["class"]

    def test_a_browser_string_is_shown_as_text(self, person) -> None:
        # Whoever signs in chooses the browser string the owner later reads.
        hostile = "<script>alert(1)</script>"
        client = browser(person, "192.0.2.10", FIREFOX)
        UserSessionFactory(user=person, ip="198.51.100.24", user_agent=hostile)

        response = client.get(reverse("usersessions_list"))

        soup = BeautifulSoup(response.content.decode(), "html.parser")
        assert soup.select("tbody script") == []
        cells = next(row for row in rows_of(response) if row[1] == "198.51.100.24")
        assert cells[2] == hostile

    def test_a_session_with_no_user_agent_is_still_listed(self, person) -> None:
        client = browser(person, "192.0.2.10", FIREFOX)
        UserSessionFactory(user=person, ip="198.51.100.24", user_agent="")

        rows = rows_of(client.get(reverse("usersessions_list")))

        assert next(row[1:3] for row in rows if row[1] == "198.51.100.24") == [
            "198.51.100.24",
            "",
        ]
        assert len(rows) == 2


class TestSigningOutOtherSessions:
    def test_the_button_posts_to_the_sessions_page(self, three_browsers) -> None:
        soup = BeautifulSoup(
            three_browsers[0].get(reverse("usersessions_list")).content.decode(),
            "html.parser",
        )

        form = soup.find("form", action=reverse("usersessions_list"))
        assert form.find("button") is not None

    def test_posting_it_leaves_only_the_posting_browsers_session(
        self, three_browsers
    ) -> None:
        response = three_browsers[1].post(reverse("usersessions_list"), follow=True)

        rows = rows_of(response)
        assert len(rows) == 1
        assert rows[0][1] == "198.51.100.24"

    def test_the_other_browsers_are_sent_to_sign_in(self, three_browsers) -> None:
        three_browsers[1].post(reverse("usersessions_list"))

        for other in (three_browsers[0], three_browsers[2]):
            response = other.get(reverse("account-center"))
            assert response.status_code == 302
            assert response["Location"].startswith(reverse("account_login"))

    def test_the_posting_browser_stays_signed_in(self, three_browsers) -> None:
        three_browsers[1].post(reverse("usersessions_list"))

        assert three_browsers[1].get(reverse("account-center")).status_code == 200


class TestSigningOutTheLastSession:
    def test_the_button_posts_to_sign_out(self, person) -> None:
        client = browser(person, "192.0.2.10", FIREFOX)

        soup = BeautifulSoup(
            client.get(reverse("usersessions_list")).content.decode(), "html.parser"
        )

        form = soup.find(
            "form", attrs={"action": reverse("account_logout"), "id": None}
        )
        assert form is not None
        assert form.find("button") is not None

    def test_posting_it_signs_the_person_out(self, person) -> None:
        client = browser(person, "192.0.2.10", FIREFOX)

        client.post(reverse("account_logout"))

        response = client.get(reverse("account-center"))
        assert response.status_code == 302
        assert response["Location"].startswith(reverse("account_login"))


class TestHostProjectOverride:
    def test_the_projects_page_is_the_one_rendered(self, person, settings) -> None:
        client = browser(person, "192.0.2.10", FIREFOX)
        override_dir = Path(__file__).parent / "templates_host_override"
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["DIRS"] = [override_dir, *templates[0]["DIRS"]]
        settings.TEMPLATES = templates

        html = client.get(reverse("usersessions_list")).content.decode()

        assert "This project's own sessions page" in html
        assert f'action="{reverse("usersessions_list")}"' not in html
