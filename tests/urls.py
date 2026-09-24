"""The suite's urlconf.

It is the demo project's routes plus whatever a test needs a route for. A
test-only view is added here rather than in ``demo/urls.py``, so the demo
project keeps only the pages a person is meant to open.
"""

from demo.urls import urlpatterns

__all__ = ["urlpatterns"]
