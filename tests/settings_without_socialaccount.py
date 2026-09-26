"""The suite's settings with allauth's social account app taken out.

For a project that keeps allauth's account pages and has no social sign-in.
Only what names the social account app is removed: its apps and its provider
configuration. Everything else is the suite's, so a difference in behaviour is
down to that app being absent.
"""

from tests.settings import *  # noqa: F403

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS  # noqa: F405
    if not app.startswith("allauth.socialaccount")
]

del SOCIALACCOUNT_PROVIDERS  # noqa: F821
