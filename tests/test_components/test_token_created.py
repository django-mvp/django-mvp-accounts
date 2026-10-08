"""The ``mvp_accounts.token.created`` component, which has no Python module."""

from bs4 import BeautifulSoup

SOURCE = (
    '<c-mvp_accounts.token.created value="{value}" header_prefix="{prefix}" '
    'done_url="/account/tokens/" />'
)


class TestTokenCreatedComponent:
    def test_the_value_is_in_the_field_with_the_expected_id(self, render) -> None:
        html = render(SOURCE.format(value="abc123def", prefix="Token"))

        field = BeautifulSoup(html, "html.parser").find(id="new-api-token")
        assert field["value"] == "abc123def"

    def test_the_header_prefix_is_in_the_example(self, render) -> None:
        html = render(SOURCE.format(value="abc123def", prefix="Bearer"))

        assert "Authorization: Bearer" in html

    def test_a_value_with_markup_in_it_is_escaped(self, render) -> None:
        html = render(
            '<c-mvp_accounts.token.created :value="value" />',
            value='"><b id="injected">',
        )

        soup = BeautifulSoup(html, "html.parser")
        assert soup.find(id="injected") is None
