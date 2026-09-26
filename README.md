# django-mvp-accounts

Sign-up, sign-in, account management and API access for
[django-mvp](https://github.com/django-mvp/django-mvp) projects, assembled from
the third-party packages that already do each of those jobs well.

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

- **Menu entries** for Email, Password and Phone number, beside its Overview entry.
- **A card for each of those pages** on the Account Center landing page, linking to it.

A page allauth has not routed gets neither. With phone numbers turned off
(`"phone"` left out of `ACCOUNT_SIGNUP_FIELDS`), there is no Phone number entry or card.
Without allauth installed the package adds nothing and raises nothing.

The Account Center itself, the "Account Center" and "Log out" entries in the user menu, and
the sign-out form are django-mvp's. Another installed app can add its own card the same way:
ship a template named `mvp/account/overview.html` that extends `mvp/account/overview.html`
and adds to `{% block account.cards %}` after `{{ block.super }}`.

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

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-accounts/blob/main/LICENSE).
