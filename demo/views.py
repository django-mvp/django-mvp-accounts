"""The demo project's pages.

Each view subclasses ``MVPTemplateView`` rather than Django's ``TemplateView``:
that is what supplies the page title, the subtitle and the breadcrumb trail the
application shell draws around the content.
"""

from mvp.views import MVPTemplateView


class OverviewView(MVPTemplateView):
    """What this package is, and what it puts on a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "What this package puts on a page"
    breadcrumbs = [{"text": "Overview"}]
