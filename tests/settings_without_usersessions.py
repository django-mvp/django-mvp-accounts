"""The suite's settings with allauth's user sessions app taken out.

For a project that keeps allauth's account pages and does not record sessions.
The app and its middleware both go: importing the middleware imports the
app's models, which raises when the app is not installed. Everything else is
the suite's, so a difference in behaviour is down to that app being absent.
"""

from tests.settings import *  # noqa: F403

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS  # noqa: F405
    if app != "allauth.usersessions"
]

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE  # noqa: F405
    if middleware != "allauth.usersessions.middleware.UserSessionsMiddleware"
]
