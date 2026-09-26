"""The suite's settings with allauth taken out, for a project that never installs it.

Only what names allauth is removed: its apps, its middleware, its
authentication backend, its adapter and its routes. Everything else is the
suite's, so a difference in behaviour is down to allauth being absent.
"""

from tests.settings import *  # noqa: F403

INSTALLED_APPS = [app for app in INSTALLED_APPS if not app.startswith("allauth")]  # noqa: F405

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE  # noqa: F405
    if not middleware.startswith("allauth")
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

ROOT_URLCONF = "tests.urls_without_allauth"

# Names the demo adapter, which imports allauth.
del ACCOUNT_ADAPTER  # noqa: F821
