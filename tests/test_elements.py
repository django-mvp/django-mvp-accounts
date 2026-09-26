"""allauth's shared elements are drawn from django-mvp's components.

allauth's pages describe their forms, buttons and alerts through elements, and
this package supplies each element's markup. The tests read the rendered pages
back, since an element that fell back to allauth's bare markup still returns
200 and still shows its form.
"""

import pytest
from bs4 import BeautifulSoup
from django.template import Context, Origin, Template
from django.urls import reverse

from tests.factories import EmailAddressFactory

MISMATCHED_SIGNUP = {
    "email": "not-an-email",
    "password1": "a-long-unusual-passphrase",
    "password2": "a-different-passphrase",
}


def soup_of(response) -> BeautifulSoup:
    return BeautifulSoup(response.content.decode(), "html.parser")


def render_element(source: str, **context) -> BeautifulSoup:
    # allauth's element tag names the template it is written in.
    origin = Origin(name="elements.html", template_name="elements.html")
    template = Template("{% load allauth %}" + source, origin=origin)
    html = template.render(Context(context))
    return BeautifulSoup(html, "html.parser")


def field_wrapper(soup: BeautifulSoup, field_id: str):
    """The block holding a field's input, label and messages."""
    return soup.find(id=field_id).find_parent("div", id=f"div_{field_id}")


def visible_inputs(soup: BeautifulSoup):
    hidden = {"hidden", "submit", "button"}
    return [i for i in soup.select("form input") if i.get("type") not in hidden]


class TestFieldErrors:
    def test_a_failed_sign_up_shows_each_error_by_its_field(self, client, db) -> None:
        response = client.post(reverse("account_signup"), MISMATCHED_SIGNUP)

        soup = soup_of(response)
        assert (
            "Enter a valid email address." in field_wrapper(soup, "id_email").get_text()
        )
        assert "same password" in field_wrapper(soup, "id_password2").get_text()

    def test_a_wrong_password_shows_allauths_form_error(self, client, db) -> None:
        address = EmailAddressFactory()

        response = client.post(
            reverse("account_login"),
            {"login": address.email, "password": "not-the-password"},
        )

        form = soup_of(response).find("form")
        assert "email address and/or password you specified" in form.get_text()


class TestAccessibleForms:
    """FR-015: every input has a label, and what it points at exists."""

    def assert_inputs_are_labelled_and_described(self, soup: BeautifulSoup) -> None:
        inputs = visible_inputs(soup)
        assert inputs, "the page has no inputs to check"
        for control in inputs:
            assert soup.find("label", attrs={"for": control["id"]}), control
            for described_by in control.get("aria-describedby", "").split():
                assert soup.find(id=described_by), (control["id"], described_by)

    @pytest.mark.parametrize("page", ["account_login", "account_signup"])
    def test_a_whole_form_is_labelled_and_described(self, client, db, page) -> None:
        soup = soup_of(client.get(reverse(page)))

        self.assert_inputs_are_labelled_and_described(soup)

    def test_a_failed_sign_up_ties_each_error_to_its_input(self, client, db) -> None:
        soup = soup_of(client.post(reverse("account_signup"), MISMATCHED_SIGNUP))

        self.assert_inputs_are_labelled_and_described(soup)
        described_by = soup.find(id="id_password2")["aria-describedby"]
        assert "same password" in soup.find(id=described_by.split()[-1]).get_text()

    def test_a_single_field_is_labelled(self, signed_in_client, rebuild_urls) -> None:
        with rebuild_urls(
            ACCOUNT_CHANGE_EMAIL=True, ACCOUNT_REAUTHENTICATION_REQUIRED=False
        ):
            response = signed_in_client.post(
                reverse("account_email"), {"email": "not-an-email", "action_add": ""}
            )

        soup = soup_of(response)
        control = soup.find("input", attrs={"name": "email"})
        assert "Enter a valid email address." in soup.get_text()
        assert soup.find("label", attrs={"for": control["id"]})

    @pytest.mark.skip(
        reason="django-mvp#412: c-form.field renders help text and errors "
        "without ids, so a single input cannot reference them"
    )
    def test_a_single_field_points_at_its_error(
        self, signed_in_client, rebuild_urls
    ) -> None:
        with rebuild_urls(
            ACCOUNT_CHANGE_EMAIL=True, ACCOUNT_REAUTHENTICATION_REQUIRED=False
        ):
            response = signed_in_client.post(
                reverse("account_email"), {"email": "not-an-email", "action_add": ""}
            )

        soup = soup_of(response)
        control = soup.find("input", attrs={"name": "email"})
        described_by = control["aria-describedby"].split()
        assert any(
            "Enter a valid email address." in soup.find(id=i).get_text()
            for i in described_by
        )


class TestButtons:
    def test_a_submit_button_is_a_theme_button(self, client, db) -> None:
        soup = soup_of(client.get(reverse("account_login")))

        submit = soup.select_one("form button[type=submit]")
        assert {"btn", "btn-primary"} <= set(submit["class"])

    def test_a_button_with_an_href_is_a_link(self, client, db) -> None:
        soup = soup_of(client.get(reverse("account_login")))

        link = soup.find("a", attrs={"href": reverse("account_request_login_code")})
        assert "btn" in link["class"]

    def test_an_href_is_escaped(self) -> None:
        soup = render_element(
            "{% element button href=href %}Go{% endelement %}",
            href='"><script>alert(1)</script>',
        )

        assert soup.find("script") is None
        assert soup.find("a")["href"] == '"><script>alert(1)</script>'

    def test_a_button_tied_to_another_form_submits_it(self) -> None:
        """allauth's "Request new code" button names a form and no type.

        It relies on the browser's default, which submits, so the element has to
        keep that default or the button does nothing when pressed.
        """
        soup = render_element(
            '{% element button form="resend" %}Request new code{% endelement %}'
        )

        button = soup.find("button", attrs={"form": "resend"})
        assert button["type"] == "submit"

    def test_a_button_group_holds_its_buttons(self) -> None:
        soup = render_element(
            "{% element button_group %}{% element button %}A{% endelement %}"
            "{% endelement %}"
        )

        assert soup.select_one("div button.btn")


class TestElementMarkup:
    @pytest.mark.parametrize(
        ("tags", "variant"),
        [("error", "alert-error"), ("warning", "alert-warning"), ("", "alert-info")],
    )
    def test_an_alert_takes_its_variant_from_its_tags(self, tags, variant) -> None:
        soup = render_element(
            "{% element alert tags=tags %}{% slot message %}Careful{% endslot %}"
            "{% endelement %}",
            tags=tags,
        )

        alert = soup.select_one("[role=alert]")
        assert variant in alert["class"]
        assert "Careful" in alert.get_text()

    def test_a_badge_is_a_theme_badge(self) -> None:
        soup = render_element(
            '{% element badge tags="success" %}Verified{% endelement %}'
        )

        assert "badge-success" in soup.select_one(".badge")["class"]

    def test_details_open_and_close(self) -> None:
        soup = render_element(
            "{% element details %}{% slot summary %}More{% endslot %}"
            "{% slot body %}Body{% endslot %}{% endelement %}"
        )

        assert soup.select_one("details summary").get_text(strip=True) == "More"
        assert "Body" in soup.select_one("details").get_text()

    def test_headings_and_text(self) -> None:
        soup = render_element(
            "{% element h1 %}One{% endelement %}{% element h2 %}Two{% endelement %}"
            "{% element p %}Text{% endelement %}{% element hr %}{% endelement %}"
        )

        assert soup.h1.get_text(strip=True) == "One"
        assert soup.h2.get_text(strip=True) == "Two"
        assert "Text" in soup.get_text()
        assert soup.select_one(".divider")

    def test_a_form_posts_to_its_action(self) -> None:
        soup = render_element(
            '{% element form method="post" action="/x/" %}{% slot body %}Hi{% endslot %}'
            "{% slot actions %}Go{% endslot %}{% endelement %}"
        )

        assert soup.form["method"] == "post"
        assert soup.form["action"] == "/x/"
