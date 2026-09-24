"""The demo project renders.

Everything in the demo fails quietly. An unresolvable Cotton component renders
as empty output, a Tailwind class the packaged stylesheet does not emit does
nothing, and a menu entry whose URL will not resolve is dropped from the tree.
None of those raise, so the demo is asserted against its rendered pages rather
than against the objects that built them.
"""

from django.urls import reverse


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        """The page is inside django-mvp's application shell, not bare.

        A template that fails to extend the shell still returns 200 and still
        shows its own content, so the status code proves nothing about this.
        """
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_holds_the_pages_that_exist(self, overview_page: str) -> None:
        """A menu entry naming a route that will not resolve is dropped.

        It is dropped silently, which is why the assertion is on the rendered
        sidebar rather than on the menu tree that produced it.
        """
        assert "Overview" in overview_page

    def test_the_starter_component_reached_the_page(self, overview_page: str) -> None:
        """Delete this test with the starter component.

        Cotton renders a component it cannot resolve as empty output, so this
        is the assertion that would catch a moved or renamed template.
        """
        assert "It renders" in overview_page
