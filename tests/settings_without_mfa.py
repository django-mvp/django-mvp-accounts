"""The suite's settings with allauth's multi-factor app taken out.

For a project that keeps allauth's account pages and has no two-factor
authentication. Only the app itself is removed. The multi-factor settings stay,
as they would in a project that turned the app off without editing its
settings, so a difference in behaviour is down to that app being absent.
"""

from tests.settings import *  # noqa: F403

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "allauth.mfa"]  # noqa: F405
