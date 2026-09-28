# Implementation Plan: Signed-in sessions

**Branch**: `004-signed-in-sessions` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

allauth's sessions page extends the account management layout FS-001 already overrides, so it
renders inside the Account Center with no page template of its own (research R1). What it draws
that this package does not reach yet is its table, so this feature adds the six table elements,
identical to the ones FS-003 adds for the security-key list, with the table scrolling sideways
inside its own area (R2). US1 adds a "Sessions" entry to the Account Center's "Account" group and
a card to its landing page, both following whether allauth routes the page (R4). The demo installs
the user sessions app with activity tracking on and gives one account three sessions (R6). No
Python in the package beyond one menu entry.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2, 6.0 and 6.1
**Primary Dependencies**: django-mvp ≥ 0.25.0 (runtime), django-allauth 65.x ≥ 65.19.4 (development only, unchanged)
**Storage**: none in the package. The demo gains allauth's user sessions table
**Testing**: pytest, pytest-django, xdist. Assertions against pages rendered through allauth's real views
**Target Platform**: any Django project built on django-mvp
**Project Type**: reusable Django app (templates plus one menu module)
**Constraints**: no import of `allauth.usersessions` from the package; every added string translatable
**Scale/Scope**: 6 element overrides, 1 menu entry, 1 card

## Constitution Check

| Article | How this plan meets it |
|---|---|
| I Test-first | Each element, entry, card and page state gets a failing render test first |
| II Simplicity | Templates and one menu entry. No page override, no guard for the user sessions app (R1, R4) |
| III Anti-abstraction | No tags, helpers or base classes. The elements are copied from FS-003, identical, so the two branches add the same files (R2) |
| IV Integration-first | Tests drive allauth's real list view and sign-out flow with real Django sessions (R5) |
| V Security | Session fields reach the page through allauth's `{{ }}`, escaped. No flow is modified. The demo's seeded sessions are behind `seed_demo`'s DEBUG guard |
| VI Documentation | README sessions section and Account Center list, `CONTEXT.md` term, CHANGELOG, each in the story that introduces it |
| VII Dependencies | None added. The user sessions app ships inside django-allauth, already a development dependency |
| VIII i18n | The menu label and card text wrapped, catalogue regenerated |
| IX Data model | No models |
| X Tests | Page tests are template tests declared in `non-mirror-paths`. `menus.py` stays with `tests/test_menus.py`. One factory for allauth's `UserSession` |
| XIII Upstream first | Signing out one chosen session is an allauth gap, not built here (D1) |
| XIV Optional capabilities | User sessions app absent: no entry, no card, no page raises (R5) |

No violations.

## Design

### Package layout

```text
mvp_accounts/
├── menus.py                          # + "Sessions" in the Account group
├── locale/en/LC_MESSAGES/django.po   # regenerated
└── templates/
    ├── allauth/elements/
    │   ├── table.html                # FS-003's, byte-identical: overflow-x-auto wrapper, .table (R2)
    │   └── thead, tbody, tr, th, td  # FS-003's, byte-identical
    └── mvp/account/overview.html     # + Sessions card
```

### Demo and tests

```text
demo/
├── settings.py                        # user sessions app, humanize, middleware, tracking on (R6)
└── management/commands/seed_demo.py   # regular.user gets two more sessions (R6)
tests/
├── settings_without_usersessions.py   # allauth kept, user sessions app and middleware stripped
├── factories.py                       # + UserSessionFactory, backed by a real Django session
├── test_sessions_page.py              # template tests, non-mirror
├── test_elements.py                   # + table elements
├── test_account_center.py             # + card
├── test_menus.py                      # + entry
├── test_demo.py                       # + seeded sessions
└── test_without_usersessions.py       # subprocess, non-mirror
```

### What every page test asserts

The four assertions FS-001's management-page tests make, unchanged: django-mvp's stylesheet is
linked; the sidebar's navigation is present; allauth's bare `<strong>Menu:</strong>` block is
absent; and allauth's markup specific to this page is present (the "Sessions" heading and the
sessions form). Reuse FS-001's helpers where the existing test modules have them.

### Story order

**US1 → US2, one at a time, in one working tree.** US2 exercises the page, factory and demo
sessions US1 builds. Both touch `tests/test_sessions_page.py`.

## Complexity Tracking

None.
