# django-mvp-access-control

Sign-up, sign-in, account management and API access for
[django-mvp](https://github.com/django-mvp/django-mvp) projects, assembled from
the third-party packages that already do each of those jobs well.

It is not usable yet. Nothing has been released, and the package does nothing
beyond installing cleanly.

## Scope and philosophy

A project built on django-mvp needs people to be able to create an account,
sign in, change their details, and get back in when they forget how. Once the
project has an API, those same people need a way to reach it — a token they can
create, see, and revoke themselves. This package is where all of that is wired
together, so each project does not do it again by hand.

It implements none of it. Accounts, sign-in, email verification and two-factor
authentication come from [django-allauth](https://allauth.org). API access
comes from [Django REST framework](https://www.django-rest-framework.org) and a
token package alongside it, and only appears when the project has installed
Django REST framework. What this package owns is the part in between: the
settings those packages need, the pages they render through django-mvp's
application shell, and the places they appear in its menus.

It is about access to your *own* account. It does not decide what a signed-in
person is allowed to do. Roles, groups, object permissions and
authorisation rules stay the host project's, and belong in a different package
if they belong in one at all.

When two designs conflict, the one that leaves more of the work to the
upstream package wins. A feature allauth or Django REST framework already has
is configured and rendered here, never rebuilt.

This package supersedes
[django-accounts-center](https://github.com/django-mvp/django-accounts-center),
which will be retired once everything it provides is available here.

## Installation

```bash
pip install django-mvp-access-control
```

Then add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp",
    "mvp_access_control",
]
```

This package requires [django-mvp](https://github.com/django-mvp/django-mvp).
It renders inside django-mvp's layout and reads its colours from the theme
django-mvp supplies, so it does nothing useful on its own.

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
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-access-control/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-access-control/blob/main/CONTEXT.md).

```bash
poetry install
poetry run pytest
poetry run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
poetry run python manage.py migrate
poetry run python manage.py seed_demo
poetry run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-access-control/blob/main/LICENSE).
