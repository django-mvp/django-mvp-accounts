"""The package installs and exposes what a consuming project needs from it."""

from pathlib import Path

from django.apps import apps

import mvp_accounts

PACKAGE_ROOT = Path(mvp_accounts.__file__).parent
COTTON_ROOT = PACKAGE_ROOT / "templates" / "cotton" / "mvp_accounts"

EXAMPLE_TAG = "c-mvp_accounts.example"


class TestPackagedApp:
    """What a host project gets after installing and adding it to INSTALLED_APPS."""

    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_accounts")

    def test_components_are_where_cotton_looks_for_them(self) -> None:
        """Cotton resolves every tag this package ships under one directory.

        The directory name is the first segment of each of those tags, so it is
        not a free choice: renaming it breaks all of them at once, and does so
        silently — a component Cotton cannot find renders as empty output
        rather than raising.
        """
        assert COTTON_ROOT.is_dir()

    def test_the_public_surface_is_the_components_it_ships(self) -> None:
        """The whole public surface, asserted rather than described.

        A component added here is a decision about this package's API, not an
        implementation detail. Listing them exactly is what makes one arrive
        deliberately, and this is the line to update when one does.
        """
        components = sorted(path.name for path in COTTON_ROOT.rglob("*.html"))
        assert components == ["example.html"]


class TestStarterComponent:
    """Delete this class along with the starter component it covers."""

    def test_it_renders_its_slot(self, render) -> None:
        markup = render(f"<{EXAMPLE_TAG}>Inside</{EXAMPLE_TAG}>")
        assert "Inside" in markup

    def test_it_renders_a_title_when_given_one(self, render) -> None:
        markup = render(f'<{EXAMPLE_TAG} title="Named" />')
        assert "Named" in markup

    def test_it_renders_no_heading_without_a_title(self, render) -> None:
        """The default is an empty string, and an empty heading is not drawn.

        Asserted as an absence as well as a presence: a component that always
        rendered the heading element would pass the test above while putting an
        empty one on every page.
        """
        markup = render(f"<{EXAMPLE_TAG}>Inside</{EXAMPLE_TAG}>")
        assert "<h2" not in markup
