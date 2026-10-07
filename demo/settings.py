"""Settings for the demo project.

A demonstration target, never deployed. It runs on the development server so
this package can be looked at in a browser while it is being built, and it is
the one description of the application shell — `tests/settings.py` inherits
from this file rather than restating it.
"""

from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-demo-project-only"

DEBUG = True

# The development server is reached over the network by hostname, not only at
# localhost. DEBUG auto-allows localhost and nothing else, so a bare list here
# answers any other hostname with 400 Bad Request.
ALLOWED_HOSTS = ["*"]

# The development server speaks plain HTTP. A cookie marked Secure is discarded
# by the browser, which leaves GET pages rendering perfectly while every form
# post comes back 403.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# First, so demo/templates/base.html wins over any library template of that
# name. A file there named after one django-mvp ships silently replaces it on
# every page.
INSTALLED_APPS = [
    "demo",
    # Ahead of allauth so its layouts and elements win, and ahead of mvp so its
    # Account Center overview is the one Django finds first.
    "mvp_accounts",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    # Records where each account is signed in, which is what allauth's
    # sessions page lists.
    "allauth.usersessions",
    # allauth's test provider: it completes a sign-in on this machine, so every
    # social account page can be reached without credentials from a real one.
    "allauth.socialaccount.providers.dummy",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # allauth's sessions page and security-key list load their date filters
    # from here, and fail to render without it.
    "django.contrib.humanize",
    # The API the demo's tokens reach, and the package that keeps the tokens.
    "rest_framework",
    "knox",
    "mvp",
    "daisy_cotton",
    "easy_icons",
    "crispy_forms",
    "mvp_forms",
    "flex_menu",
    "django_cotton",
    # Reloads the browser on a change to a template, a stylesheet or Python. It
    # arrives with the shared development bundle rather than a pin of its own,
    # and its middleware removes itself from the chain unless DEBUG is on.
    "django_browser_reload",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # The shell puts the site's name in every page title, reading it from
    # request.site. This middleware is what puts it there.
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # With activity tracking on, keeps each recorded session's address,
    # browser and last-seen time current on every request.
    "allauth.usersessions.middleware.UserSessionsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Last, because it rewrites the response body to insert its script tag and
    # anything that encodes or compresses the body has to run after it.
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mvp.context_processors.mvp_config",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS: list[dict] = []

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Codes and links are kept for the outbox page rather than sent anywhere.
EMAIL_BACKEND = "demo.mail.OutboxEmailBackend"

# What a typical project runs. The tests reach the other half of each choice
# by overriding the setting, and rebuild allauth's URLconf where needed.
ACCOUNT_ADAPTER = "demo.adapter.DemoAccountAdapter"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*", "phone"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_REAUTHENTICATION_REQUIRED = True

# Passkey sign-up stays off: allauth allows it only with mandatory email
# verification by code. Security keys and passkeys need HTTPS or `localhost`.
# The fixed code is accepted only with DEBUG on, and the demo is never deployed.
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes", "webauthn"]
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_TRUST_ENABLED = True
MFA_TOTP_INSECURE_BYPASS_CODE = "123456"

# The sessions page can show when each session was last used. The demo turns
# it on so that column can be seen; the package leaves it to the project.
USERSESSIONS_TRACK_ACTIVITY = True

# A token is what the demo's API accepts. knox's own default lifetime is ten
# hours, which suits a browser and not a script, so tokens here last thirty
# days and a person may hold five.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["knox.auth.TokenAuthentication"],
}
REST_KNOX = {
    "TOKEN_TTL": timedelta(days=30),
    "TOKEN_LIMIT_PER_USER": 5,
}

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]
CRISPY_TEMPLATE_PACK = "daisyui"

FLEX_MENUS = {
    "renderers": {
        "sidebar": "mvp.renderers.SidebarRenderer",
        "dock": "mvp.renderers.MobileFooterNavRenderer",
    },
    "log_url_failures": DEBUG,
}

# Icons are referenced by name. django-mvp's pack covers the names the shell
# uses for itself; anything this project names goes on top of it. An
# unregistered name raises rather than drawing nothing.
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "packs": ["mvp.utils.BS5_ICONS"],
        "icons": {
            "overview": "bi bi-house",
            # A provider button draws the icon named after its provider id. The
            # package ships none: the project supplies one per provider it lists.
            "dummy": "bi bi-person-badge",
        },
    },
}

# Deep-merged over django-mvp's defaults, so only the differences appear here.
MVP_CONFIG = {
    "layout": {
        "sidebar": {
            "title": "django-mvp-accounts",
        },
    },
    "theme": {
        # Several to switch between, so what this package renders can be looked
        # at light and dark without editing a setting.
        "choices": ["light", "dark", "corporate", "dracula"],
    },
}

STATIC_URL = "/static/"

USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
