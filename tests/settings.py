"""Django settings for testing django-mvp-accounts.

The application configuration — INSTALLED_APPS, MIDDLEWARE, TEMPLATES,
EASY_ICONS, FLEX_MENUS, MVP_CONFIG — lives in ``demo/settings.py`` and is
inherited here rather than restated.

Restating it would mean two descriptions of one application shell, and the
failure that produces is the quiet one: the suite stays green against its own
copy while the project a reader actually opens is broken. Cotton resolves a
component it cannot find to empty output, so that break leaves no error
anywhere.

Only what a test run needs differently is set below.
"""

from demo.settings import *  # noqa: F403

SECRET_KEY = "django-insecure-test-key-for-mvp_accounts-tests-only"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# The demo keeps a file on disk so its data survives a restart. A test run
# wants neither the file nor the history.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# The demo's routes, behind a urlconf of the suite's own so a test-only route
# has somewhere to go.
ROOT_URLCONF = "tests.urls"

# Templates that exist only to put something in one exact situation a test
# needs. They are not part of the demo project and are never distributed.
TEMPLATES[0]["DIRS"] = [BASE_DIR / "tests" / "templates"]  # noqa: F405

# The demo lists the test provider alone. The pages that draw provider buttons
# are asserted with two, so the suite adds GitHub, whose app is configured here
# rather than in the database and whose icon django-mvp's pack already names.
INSTALLED_APPS = [*INSTALLED_APPS, "allauth.socialaccount.providers.github"]  # noqa: F405

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APPS": [{"client_id": "suite-client-id", "secret": "suite-secret"}],
    },
}

# The demo accepts a fixed authenticator code. Every test enters a real one
# computed from the secret, so the shortcut is switched off here.
MFA_TOTP_INSECURE_BYPASS_CODE = None

# The demo lets in staff only. The suite runs the package's default, every
# signed-in person, and the tests of the setting name a function themselves.
del MVP_ACCOUNTS_API_TOKEN_ACCESS  # noqa: F821
