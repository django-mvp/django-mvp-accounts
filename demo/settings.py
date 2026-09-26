"""Settings for the demo project.

A demonstration target, never deployed. It runs on the development server so
this package can be looked at in a browser while it is being built, and it is
the one description of the application shell — `tests/settings.py` inherits
from this file rather than restating it.
"""

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

# This project's own apps come first so its templates win over any the
# libraries ship under the same name, which is how demo/templates/base.html
# reaches the pages that extend "base.html". Take care adding to that
# directory: a file named after one django-mvp ships replaces it everywhere,
# silently, for every page in the demo.
INSTALLED_APPS = [
    "demo",
    # Ahead of allauth so its layouts and elements win, and ahead of mvp so its
    # Account Center overview is the one Django finds first.
    "mvp_accounts",
    "allauth",
    "allauth.account",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "mvp",
    "easy_icons",
    "crispy_forms",
    "crispy_tailwind",
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

# What a typical project runs: sign in by email, a link to verify it, a code as
# an alternative to the password, phone numbers stored by the demo's adapter,
# and a fresh sign-in before anything sensitive changes. The tests reach the
# other halves of each choice by rebuilding allauth's URLconf.
ACCOUNT_ADAPTER = "demo.adapter.DemoAccountAdapter"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*", "phone"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_REAUTHENTICATION_REQUIRED = True

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["tailwind"]
CRISPY_TEMPLATE_PACK = "tailwind"

# Which class draws the sidebar tree declared in demo/menus.py, and which draws
# the dock shown below the sidebar breakpoint.
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
