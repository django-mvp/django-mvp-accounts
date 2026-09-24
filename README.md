# django-mvp-accounts

Sign-up, sign-in, account management and API access for
[django-mvp](https://github.com/django-mvp/django-mvp) projects, assembled from
the third-party packages that already do each of those jobs well.

It is not usable yet. Nothing has been released, and the package does nothing
beyond installing cleanly.

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

```bash
pip install django-mvp-accounts
```

Then add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp",
    "mvp_accounts",
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
