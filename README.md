# django-mvp-accounts

Sign-up, sign-in, account management and API access for
[django-mvp](https://github.com/django-mvp/django-mvp) projects, built from the
third-party packages that already do each job well.

It is not released yet. So far it puts django-allauth's sign-in, sign-up and
sign-out pages inside django-mvp's application shell.

## Scope & philosophy

A project built on django-mvp needs people to be able to create an account,
sign in, change their details, and get back in when they forget how. Once the
project has an API, those same people need a way to reach it: a token they can
create, see and revoke themselves. This package is where that is wired into
django-mvp, so each project does not do it again by hand.

It implements none of it. Accounts, sign-in and recovery come from an existing
Django authentication package, and API tokens come from
[Django REST framework](https://www.django-rest-framework.org) and a token
package alongside it. The package is not tied to one authentication package,
but [django-allauth](https://allauth.org) is the only one supported for now.
What this package owns is the part in between: the pages those packages render
through django-mvp's application shell, and the places they appear in its menus.
What appears depends on what the project has installed. Nothing shows up for a
package or a feature the project has not turned on.

It is about access to your *own* account. It does not decide what a signed-in
person is allowed to do: roles, groups, object permissions and authorisation
rules stay the host project's. Handling people's data rights, such as producing
what a site holds about someone, belongs to
[django-mvp-compliance](https://github.com/django-mvp/django-mvp-compliance).

When two designs conflict, the one that leaves more of the work to the
integrated package wins. A feature it already has is rendered here, never
rebuilt. Adopting this package should take as little as possible, and each
integrated package is supported at its latest release wherever that can be
done.

This package supersedes
[django-accounts-center](https://github.com/django-mvp/django-accounts-center),
which will be retired once everything it provides is available here.

## Installation

Install the package and [django-allauth](https://allauth.org), which renders
the account pages this package restyles:

```bash
pip install django-mvp-accounts "django-allauth>=65.19.4,<66"
```

This package works with django-allauth 65.19.4 up to, but not including, 66. It
requires [django-mvp](https://github.com/django-mvp/django-mvp) as well, since
it renders inside django-mvp's layout and reads its colours from the theme
django-mvp supplies.

Add it to `INSTALLED_APPS` ahead of both `allauth` and `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp_accounts",
    "allauth",
    "allauth.account",
    "mvp",
]
```

The order matters. This package replaces templates that allauth and django-mvp
each ship, and Django takes a template from the first installed app that has
one by that name. Listed after either of them, this package's version is never
reached and the pages look as they did before.

Then include allauth's URLs and django-mvp's, and set allauth up as its own
[quickstart](https://docs.allauth.org/en/latest/installation/quickstart.html)
describes:

```python
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("", include("mvp.urls")),
]
```

Nothing about that setup is checked or configured for you. This package adds no
system check and sets no default, so allauth's middleware, authentication
backend and settings are yours to choose.

## What appears in the Account Center

With django-allauth installed, this package adds to django-mvp's Account Center:

- **Menu entries** for Email, Password, Phone number, Connected accounts, Two-factor
  authentication and Sessions, listed under an "Account" heading below its Overview entry.
- **A card for each of those pages** on the Account Center landing page, linking to it.

API tokens join the same entries and cards when the project has turned them on, with or
without allauth (see [API tokens](#api-tokens)).

A page allauth has not routed gets neither. With phone numbers turned off
(`"phone"` left out of `ACCOUNT_SIGNUP_FIELDS`), there is no Phone number entry or card.
Connected accounts appears only with the social account app (`allauth.socialaccount`)
installed, Two-factor authentication only with the multi-factor app (`allauth.mfa`)
installed, and Sessions only with the user sessions app (`allauth.usersessions`) installed.
Without allauth installed the package adds none of those and raises nothing; the API tokens
entry and card, which need nothing from allauth, are the only ones it can still add.

allauth's account management pages (email, change email, password change and set, phone
change and verification, connected accounts, sessions, and re-authentication) render in the
Account Center, inside the shell with its sidebar and messages. Pages that allauth builds on its entrance base render the same way
for a signed-in person, so re-authentication and the phone verification that follows a change are
management pages, while phone verification during sign-up stays an entrance page. The social
sign-in pages, including the confirmation a signed-in person sees when connecting another
account, always render as entrance pages.

The Account Center itself, the "Account Center" and "Log out" entries in the user menu, and
the sign-out form are django-mvp's. Another installed app can add its own card the same way:
ship a template named `mvp/account/overview.html` that extends `mvp/account/overview.html`
and adds to `{% block account.cards %}` after `{{ block.super }}`.

## API tokens

A person can see and manage their own API tokens in the Account Center when the project uses
[django-rest-knox](https://github.com/jazzband/django-rest-knox), which keeps the tokens but ships
no pages for them. This package adds the pages, an "API tokens" entry under the "Account" heading
and an "API tokens" card on the landing page. The pages are signed-in only, and a visitor is sent
to sign in.

Nothing is on until the project turns it on:

1. Install the `api` extra, which brings in Django REST framework 3.16 or later and
   django-rest-knox 5:

   ```bash
   pip install "django-mvp-accounts[api]"
   ```

2. Add both to `INSTALLED_APPS` and run `migrate`, which creates knox's token table:

   ```python
   INSTALLED_APPS = [
       # ...
       "rest_framework",
       "knox",
   ]
   ```

3. Include the pages' routes at an address of your choice, as the demo does:

   ```python
   urlpatterns = [
       # ...
       path("account/tokens/", include("mvp_accounts.tokens.urls")),
       path("", include("mvp.urls")),
   ]
   ```

4. Make your API accept the tokens, in your own settings, as
   [knox documents](https://jazzband.co/projects/django-rest-knox):

   ```python
   REST_FRAMEWORK = {
       "DEFAULT_AUTHENTICATION_CLASSES": ["knox.auth.TokenAuthentication"],
   }
   ```

The routes are served by `TokensView`, `CreateTokenView` and `RevokeTokenView` in
`mvp_accounts.tokens.views`, which share `TokenPageMixin`. Include the routes as above rather
than the views, so that the pages and their names stay together.

None of that is checked or configured for you: the package adds no system check and sets no
default, so a missing route or setting shows as the entry and card not appearing, or as tokens
your API does not accept. The package adds no model and no migration of its own.

The entry and the card are drawn only where the tokens routes resolve. A project that has not
installed django-rest-knox or Django REST framework, or has not included the routes, gets neither,
and the rest of the package works as before.

### Creating a token

The create page asks for a lifetime: 7 days, 30 days, 90 days, 1 year or never, with 30 days
selected. The lifetime is the token's expiry, and "never" stores none. The list is fixed in the
package. The page's form is `CreateTokenForm` in `mvp_accounts.tokens.forms`: its `lifetime`
field holds the choice, and `get_expiry()` turns a valid choice into a `timedelta`, or `None`
for "never".

A new token is shown once. The page the person returns to after creating it holds the complete
value, and no later page does: the package stores nothing but what django-rest-knox keeps, which
is a digest and the token's first characters. A person who loses a token revokes it and creates
another. The value travels from the create page to the tokens page in a signed cookie that lasts a
minute, is sent only to the tokens page and is deleted as the page shows it. Tokens carry no name
and no last-used time.

Two of knox's settings matter here:

- `TOKEN_TTL` reaches only the tokens knox's own views create. The create page passes the chosen
  lifetime instead.
- `TOKEN_LIMIT_PER_USER` is the number of working tokens a person may hold, and the pages honour
  it: at the limit the create page creates nothing and returns to the tokens page with a message,
  and the tokens page stops offering to create one. A token that has expired does not count, and
  one with no expiry does. knox sets no limit by default, so a project should set one:

  ```python
  REST_KNOX = {
      "TOKEN_LIMIT_PER_USER": 5,
  }
  ```

A request carries the token in the `Authorization` header, as `Authorization: Token <token>`.
The word before the token is knox's `AUTH_HEADER_PREFIX`, and the page shows the one your project
uses. The demo answers at `/api/whoami/` with the email of the person the token belongs to.

## Two-factor authentication

To offer two-factor authentication, install allauth's multi-factor app with its `mfa`
extra (`pip install "django-allauth[mfa]"`), add `allauth.mfa` to `INSTALLED_APPS`, and run
`migrate`. Which factors are on is your choice, through allauth's own settings:
`MFA_SUPPORTED_TYPES` (authenticator app, recovery codes and security keys),
`MFA_PASSKEY_LOGIN_ENABLED`, `MFA_TRUST_ENABLED` and the rest. This package sets none of
them and checks none of them.

Once `allauth.mfa` is installed, its pages render in django-mvp's shell:

- The two-factor overview, activating and deactivating the authenticator app, and viewing,
  downloading and generating recovery codes are management pages in the Account Center, with
  the Two-factor authentication entry and card described above.
- A page with no factor it can offer leaves that factor out. With `"totp"` missing from
  `MFA_SUPPORTED_TYPES`, nothing on the overview offers the authenticator app.
- With `"webauthn"` in `MFA_SUPPORTED_TYPES`, the security-key pages (the list, adding,
  renaming and removing a key, and re-authenticating with one) are management pages too. The
  list also needs `django.contrib.humanize` in `INSTALLED_APPS`, which allauth's page loads.
- Signing in with a passkey (`MFA_PASSKEY_LOGIN_ENABLED`) adds a "Sign in with a passkey" button
  to the sign-in page. Creating an account with a passkey (`MFA_PASSKEY_SIGNUP_ENABLED`) adds
  its own sign-up page and a page to create the passkey. allauth refuses to start with it unless
  `webauthn` is in `MFA_SUPPORTED_TYPES`, `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`,
  `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True` and `ACCOUNT_SIGNUP_FIELDS` requires
  `email*`. All four are your project's settings, and the demo leaves passkey sign-up off. Sign-in and sign-up pages are entrance pages. Every
  page keeps the ids and data attributes allauth's JavaScript looks for.
- The QR code is always drawn dark on white, in every theme, because a scanner cannot read
  it from a dark background.
- Security keys and passkeys work only over HTTPS or on `localhost`. On any other address the
  browser refuses them, whatever this package renders.

Without `allauth.mfa` installed, the Account Center has no Two-factor authentication entry or
card, and nothing else changes.

## Signed-in sessions

allauth's sessions page lists the browsers and devices a person is signed in from,
and it renders in the Account Center like the other management pages. This
package adds a Sessions entry and card for it, and draws its table with
django-mvp's table class inside a wrapper that scrolls sideways on a narrow
screen. To turn the page on, install allauth's user sessions app, its
middleware and `django.contrib.humanize`, which allauth's page loads its date
filters from, as
[allauth documents](https://docs.allauth.org/en/latest/usersessions/index.html):

```python
INSTALLED_APPS = [
    # ...
    "allauth.usersessions",
    "django.contrib.humanize",
]

MIDDLEWARE = [
    # ...
    "allauth.account.middleware.AccountMiddleware",
    "allauth.usersessions.middleware.UserSessionsMiddleware",
]
```

Set `USERSESSIONS_TRACK_ACTIVITY = True` to add a "Last seen at" column. The
package leaves the setting to the project.

Only sessions allauth has recorded are listed. A browser that was already signed
in before the app was installed appears after its next sign-in, or after its
next request when activity tracking is on. The page offers one action: signing
out every session except the current one, without asking first, as allauth's
does. Signing out one chosen session is not offered, because allauth does not
offer it.

Without the user sessions app the Account Center has no Sessions entry or card,
and nothing else changes.

## Signing in with other accounts

To offer sign-in with GitHub, Google or another provider, install
`allauth.socialaccount` and each provider's app, and configure them as
[allauth documents](https://docs.allauth.org/en/latest/socialaccount/index.html).
Nothing about that is checked or configured for you.

The social sign-in pages render as django-mvp entrance pages, like the rest of
allauth's sign-in pages. The sign-in and sign-up pages show one button for each
provider allauth lists, with the provider's name as its text.

Each button's icon is named after allauth's provider id (`github`, `google`),
so the project's [django-easy-icons](https://github.com/django-mvp/django-easy-icons)
setup needs an icon under each id of a provider it configures:

```python
EASY_ICONS = {
    "default": {
        # ...
        "icons": {
            "google": "bi bi-google",
        },
    },
}
```

What a missing icon does is django-easy-icons' decision. `EASY_ICONS_FAIL_SILENTLY`
defaults to the value of `DEBUG`, so with `DEBUG` off a missing icon raises and
breaks the sign-in and sign-up pages, and with it on (or the setting turned on) the
button shows its name alone. This package ships no provider icons and checks for none.
The OpenID buttons, one for each brand, all use the `openid` icon.

## Quickstart

<!--
  The smallest complete example: what goes in the view, what goes in the
  template, and what appears on the page. Real code that runs, not a sketch.
  If the example needs three files, show three files.
-->

## Public surface

<!--
  Everything a host project can touch: components and their attributes,
  settings, template tags, models, views. Being able to list it exhaustively is
  a feature of a package this size, and the list is what makes an addition to
  it a deliberate decision rather than a side effect.
-->

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-accounts/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-accounts/blob/main/CONTEXT.md).

```bash
uv sync
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

`seed_demo` creates accounts you can sign in with, all with the password `password`:
`regular.user@example.com`, `staff.user@example.com`, `super.user@example.com` and
`mfa.user@example.com`. The last one has an authenticator app and recovery codes, so
signing in ends at the second-factor step. The demo sets `MFA_TOTP_INSECURE_BYPASS_CODE`
to `123456`, so that code passes the step without a phone. That is a convenience for
this demo only: allauth refuses the setting when `DEBUG` is off, and a project of your
own should not copy it.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-accounts/blob/main/LICENSE).
