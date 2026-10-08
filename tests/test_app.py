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
        assert COTTON_ROOT.is_dir()

    def test_the_public_surface_is_the_components_it_ships(self) -> None:
        components = sorted(path.name for path in COTTON_ROOT.rglob("*.html"))
        assert components == ["created.html", "example.html"]


class TestStarterComponent:
    def test_it_renders_its_slot(self, render) -> None:
        markup = render(f"<{EXAMPLE_TAG}>Inside</{EXAMPLE_TAG}>")
        assert "Inside" in markup

    def test_it_renders_a_title_when_given_one(self, render) -> None:
        markup = render(f'<{EXAMPLE_TAG} title="Named" />')
        assert "Named" in markup

    def test_it_renders_no_heading_without_a_title(self, render) -> None:
        markup = render(f"<{EXAMPLE_TAG}>Inside</{EXAMPLE_TAG}>")
        assert "<h2" not in markup
