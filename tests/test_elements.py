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
        errors = response.context["form"].errors
        assert errors["email"][0] in field_wrapper(soup, "id_email").get_text()
        assert errors["password2"][0] in field_wrapper(soup, "id_password2").get_text()

    def test_a_wrong_password_shows_allauths_form_error(self, client, db) -> None:
        address = EmailAddressFactory()

        response = client.post(
            reverse("account_login"),
            {"login": address.email, "password": "not-the-password"},
        )

        form = soup_of(response).find("form")
        error = response.context["form"].non_field_errors()[0]
        assert error in form.get_text()


class TestAccessibleForms:
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
        response = client.post(reverse("account_signup"), MISMATCHED_SIGNUP)
        soup = soup_of(response)

        self.assert_inputs_are_labelled_and_described(soup)
        described_by = soup.find(id="id_password2")["aria-describedby"]
        error = response.context["form"].errors["password2"][0]
        assert error in soup.find(id=described_by.split()[-1]).get_text()

    def test_a_single_field_is_labelled(self, signed_in_client, rebuild_urls) -> None:
        with rebuild_urls(
            ACCOUNT_CHANGE_EMAIL=True, ACCOUNT_REAUTHENTICATION_REQUIRED=False
        ):
            response = signed_in_client.post(
                reverse("account_email"), {"email": "not-an-email", "action_add": ""}
            )

        soup = soup_of(response)
        control = soup.find("input", attrs={"name": "email"})
        assert soup.find("label", attrs={"for": control["id"]})

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
        error = response.context["form"].errors["email"][0]
        assert any(error in soup.find(id=i).get_text() for i in described_by)


class TestButtons:
    def test_a_submit_button_is_a_theme_button(self, client, db) -> None:
        soup = soup_of(client.get(reverse("account_login")))

        submit = soup.select_one("form button[type=submit]")
        assert "btn" in submit["class"]

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


class TestPanel:
    def test_it_draws_a_card_with_its_title_and_body(self) -> None:
        soup = render_element(
            "{% element panel %}{% slot title %}Authenticator App{% endslot %}"
            "{% slot body %}Not active.{% endslot %}{% endelement %}"
        )

        card = soup.select_one(".card")
        assert "Authenticator App" in card.get_text()
        assert "Not active." in card.get_text()

    def test_it_draws_every_action(self) -> None:
        soup = render_element(
            "{% element panel %}{% slot title %}Codes{% endslot %}"
            "{% slot actions %}<a href='/view/'>View</a>{% endslot %}"
            "{% slot actions %}<a href='/download/'>Download</a>{% endslot %}"
            "{% endelement %}"
        )

        hrefs = [a["href"] for a in soup.select(".card a")]
        assert hrefs == ["/view/", "/download/"]

    def test_a_panel_without_actions_draws_no_footer_links(self) -> None:
        soup = render_element(
            "{% element panel %}{% slot title %}Keys{% endslot %}{% endelement %}"
        )

        assert soup.select(".card a") == []


class TestImg:
    def test_it_draws_the_image_with_its_source_and_alt(self) -> None:
        soup = render_element(
            "{% element img src=src alt=alt %}{% endelement %}",
            src="data:image/svg+xml;base64,AAAA",
            alt="A secret",
        )

        img = soup.find("img")
        assert img["src"] == "data:image/svg+xml;base64,AAAA"
        assert img["alt"] == "A secret"

    def test_the_source_and_alt_are_escaped(self) -> None:
        soup = render_element(
            "{% element img src=src alt=alt %}{% endelement %}",
            src='"><script>alert(1)</script>',
            alt='"><script>alert(2)</script>',
        )

        assert soup.find("script") is None
        assert soup.find("img")["src"] == '"><script>alert(1)</script>'
        assert soup.find("img")["alt"] == '"><script>alert(2)</script>'

    def test_an_image_without_alt_has_no_alt_attribute(self) -> None:
        soup = render_element("{% element img src=src %}{% endelement %}", src="/a.png")

        assert soup.find("img").get("alt") is None


class TestFieldTextarea:
    SOURCE = (
        '{% element field id="recovery_codes" type="textarea" rows=2 readonly=True %}'
        "{% slot label %}Unused codes{% endslot %}"
        "{% slot value %}abc-1\nabc-2{% endslot %}{% endelement %}"
    )

    def test_it_draws_a_readonly_textarea_with_its_id_rows_and_content(self) -> None:
        textarea = render_element(self.SOURCE).find("textarea")

        assert textarea["id"] == "recovery_codes"
        assert textarea.has_attr("readonly")
        assert textarea["rows"] == "2"
        assert textarea.get_text() == "abc-1\nabc-2"

    def test_it_keeps_the_label(self) -> None:
        soup = render_element(self.SOURCE)

        label = soup.find("label", attrs={"for": "recovery_codes"})
        assert label.get_text(strip=True) == "Unused codes"

    def test_the_content_is_escaped(self) -> None:
        soup = render_element(
            '{% element field id="x" type="textarea" %}'
            "{% slot value %}{{ value }}{% endslot %}{% endelement %}",
            value="<script>alert(1)</script>",
        )

        assert soup.find("script") is None


class TestFormId:
    def test_a_form_keeps_the_id_it_is_given(self) -> None:
        soup = render_element(
            '{% element form id="webauthn_form" method="post" %}'
            "{% slot body %}Hi{% endslot %}{% endelement %}"
        )

        assert soup.form["id"] == "webauthn_form"

    def test_a_form_without_an_id_writes_none(self) -> None:
        soup = render_element(
            '{% element form method="post" %}{% slot body %}Hi{% endslot %}'
            "{% endelement %}"
        )

        assert not soup.form.has_attr("id")


class TestTableElements:
    TABLE = (
        "{% element table %}"
        "{% element thead %}{% element tr %}"
        "{% element th %}Started{% endelement %}"
        '{% element th align="right" %}Size{% endelement %}'
        "{% endelement %}{% endelement %}"
        "{% element tbody %}{% element tr %}"
        "{% element td %}Today{% endelement %}"
        '{% element td align="right" %}4{% endelement %}'
        "{% endelement %}{% endelement %}"
        "{% endelement %}"
    )

    def test_a_table_is_a_theme_table(self) -> None:
        soup = render_element(self.TABLE)

        assert "table" in soup.select_one("table")["class"]

    def test_the_head_and_body_cells_are_kept(self) -> None:
        soup = render_element(self.TABLE)

        assert [th.get_text(strip=True) for th in soup.select("thead th")] == [
            "Started",
            "Size",
        ]
        assert [td.get_text(strip=True) for td in soup.select("tbody td")] == [
            "Today",
            "4",
        ]

    def test_a_cell_aligned_right_is_aligned_to_the_end(self) -> None:
        soup = render_element(self.TABLE)

        first, second = soup.select("tbody td")
        assert second["class"] == ["text-end"]
        assert not first.has_attr("class")
