# Implementation Plan: Accounts, sign-in and recovery on the site's own pages

**Branch**: `001-allauth-account-pages` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

allauth's account pages render inside the host project's django-mvp shell because this package
overrides allauth's three layout templates and its shared elements. Entrance pages extend
django-mvp's entrance page, management pages extend the Account Center's layout, and allauth's
forms, fields, buttons and alerts are rebuilt from django-mvp's components. The package adds an
entry per management page to the Account Center's menu and a card per management page to its
landing page, both only when allauth is installed and only for pages allauth has turned on. No
Python runs at request time apart from the menu entries, allauth is a development dependency, and
nothing checks how a project configured it.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2, 6.0 and 6.1
**Primary Dependencies**: django-mvp ≥ 0.25.0 (runtime), django-allauth 65.x ≥ 65.19.4 (development only)
**Storage**: none in the package. The demo adds one demo-only model for phone numbers (R7)
**Testing**: pytest, pytest-django, xdist. Assertions against rendered pages through the test client
**Target Platform**: any Django project built on django-mvp
**Project Type**: reusable Django app (templates plus one menu module)
**Constraints**: no runtime import of allauth outside code that runs only when it is installed (Article XIV applied to allauth); every added string translatable
**Scale/Scope**: about 30 allauth pages, 12 element overrides, 3 layouts, 3 page-level overrides, 3 menu entries, 3 cards

## Constitution Check

| Article | How this plan meets it |
|---|---|
| I Test-first | Every page gets a failing render test before its layout or element exists |
| II Simplicity | Template overrides only. One Python module (`menus.py`) and one `ready()` hook |
| III Anti-abstraction | No base classes, registries or tags. Cards resolve their own URLs in the template |
| IV Integration-first | Tests drive allauth's real views through the demo's URLconf |
| V Security | No hand-built interpolation. The demo's known passwords stay behind `seed_demo`'s DEBUG guard. Sign-in and recovery flows are allauth's, unmodified |
| VI Documentation | README adoption section, CHANGELOG, `CONTEXT.md` correction, in the story that introduces each |
| VII Dependencies | allauth in the development group only (R9). django-mvp floor raised with a stated reason (R10) |
| VIII i18n | Menu labels and card text wrapped; `locale/en/` catalogue shipped |
| IX Data model | The package has no models. The demo's phone model is demo-only and indexed on its one-to-one user key |
| X Tests | Template tests are exempt from mirroring and are declared in `non-mirror-paths`. `menus.py` → `tests/test_menus.py` |
| XI Cohesion | No module-level function groups introduced |
| XIII Upstream does the work | Every page, form and flow is allauth's. The package overrides templates and nothing else |
| XIV Optional capabilities | allauth absent: package imports, menus build, pages render (R8) |
| XV Scope | No permissions, no OAuth |

No violations.

## Design

### Package layout

```text
mvp_accounts/
├── apps.py                      # ready(): import menus when allauth.account is installed
├── menus.py                     # AccountCenterMenu entries: Email, Password, Phone
├── locale/en/LC_MESSAGES/django.po
└── templates/
    ├── allauth/
    │   ├── layouts/base.html        # → entrance layout (R1)
    │   ├── layouts/entrance.html    # extends mvp/entrance.html (R2)
    │   ├── layouts/manage.html      # extends mvp/account/base.html (R3)
    │   └── elements/*.html          # built on django-mvp components (R4)
    ├── account/
    │   ├── base_entrance.html       # management layout when signed in (R1)
    │   ├── logout.html              # allauth's page, entrance parent (R1)
    │   └── verified_email_required.html  # allauth's page, entrance parent (R1)
    └── mvp/account/overview.html    # cards chained onto account.cards (R5)
```

### Demo and tests

```text
demo/
├── settings.py        # allauth installed and configured (R7)
├── urls.py            # allauth.urls at accounts/, mvp.urls at the root
├── adapter.py         # stores phone numbers, prints codes
├── models.py          # PhoneNumber, demo-only
├── migrations/0001_initial.py
└── management/commands/seed_demo.py   # + verified primary email per account
tests/
├── settings_without_allauth.py
├── test_menus.py
├── test_apps.py
├── test_entrance_pages.py      # template tests, non-mirror
├── test_recovery_pages.py      # template tests, non-mirror
├── test_account_center.py      # template tests, non-mirror
├── test_management_pages.py    # template tests, non-mirror
├── test_elements.py            # template tests, non-mirror
└── test_without_allauth.py     # subprocess (R8), non-mirror
```

### What every page test asserts

A page falling back to allauth's bare markup still returns 200 and still shows its form, so the
status code proves nothing (SC-001). Each page test asserts, on the rendered response:

1. the shell is present: django-mvp's stylesheet link;
2. entrance pages: the shell's navigation is absent (`aria-label="Main navigation"` not in the
   page, and no sidebar). Management pages: the sidebar's navigation menu is present, which is
   the Account Center's ("Account navigation") on the pages its menu claims and the main menu on
   the others (research R3). The assertion looks for the sidebar's navigation, not a label;
3. allauth's bare layout is absent: its `<strong>Menu:</strong>` block;
4. allauth's form for that page is present, by a field name or action URL specific to it.

### Behaviours a project can turn off (SC-004)

A shared fixture rebuilds allauth's URLconf under changed settings (R6). For each of code
sign-in, code reset, code verification and phone numbers, a test turns it off and asserts that
nothing on the sign-in page, the Account Center menu or its cards offers it. Sign-up closed is
checked by the sign-up page rendering allauth's closed page. allauth's sign-in page links to
sign-up whether or not it is open (`account/login.html:11-19`), and the package adds nothing to
that link (decisions, *What "offers" means when sign-up is closed*).

### Story order

**US1 → US2 → US3 → US4, one at a time, in one working tree.** US1 lays the demo, the layouts
and the elements every later story's tests run against. US2 is almost entirely tests over US1's
layout. US3 and US4 both touch the Account Center and share the URL-rebuilding fixture.

## Complexity Tracking

None.
