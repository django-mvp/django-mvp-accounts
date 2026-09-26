# ADR 0002 — Account management lives in django-mvp's Account Center

**Status:** accepted

## Decision

The account overview is django-mvp's Account Center landing page. This package adds to it rather
than building a page of its own:

- one `AccountCenterMenu` entry per management page, from `mvp_accounts/menus.py`;
- one card per management page, from `mvp_accounts/templates/mvp/account/overview.html`, which
  extends the template of the same name and adds to `{% block account.cards %}` through
  `{{ block.super }}`.

An entry or card whose allauth URL does not resolve is not drawn, so what appears follows what the
project has turned on in allauth. `menus.py` adds nothing unless `allauth.account` is installed.

The user menu's "Account Center" and "Log out" entries are django-mvp's own, and this package adds
none.

## Why

django-mvp already draws the Account Center, its navigation and the user menu's way into it, and
documents the card block as the place an installed app contributes. A second overview would give a
signed-in person two places to manage the same account. Chaining onto the card block lets later
features (two-factor authentication, sessions, connected accounts, API tokens) add their cards
without changing the ones already there.

allauth decides which account pages exist when its URLconf is imported, so asking whether a URL
resolves is the one test that always agrees with allauth. Reading allauth's settings instead would
repeat its logic and drift from it.

## Revisit if

django-mvp withdraws the Account Center or its card block, or a project needs account management
without django-mvp's URLs mounted.
