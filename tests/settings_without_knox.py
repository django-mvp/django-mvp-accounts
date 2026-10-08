"""The suite's settings with django-rest-knox and Django REST framework taken out.

Only what names either is removed: their apps, their settings and the routes
that reach the tokens pages. Everything else is the suite's, so a difference in
behaviour is down to the two packages being absent.
"""

from tests.settings import *  # noqa: F403

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS  # noqa: F405
    if app not in {"knox", "rest_framework"}
]

ROOT_URLCONF = "tests.urls_without_knox"

del REST_FRAMEWORK  # noqa: F821
del REST_KNOX  # noqa: F821
