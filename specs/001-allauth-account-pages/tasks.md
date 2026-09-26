# Tasks — 001 Accounts, sign-in and recovery on the site's own pages

**Branch**: `001-allauth-account-pages` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it.

## Order

**US1 → US2 → US3 → US4, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — Sign up, sign in and sign out on the site's own pages (P1)

Issue: #10. Delivers FR-001, FR-002, FR-004, FR-005, FR-009 to FR-013 and FR-015, and US1's part
of SC-001, SC-002, SC-004 and SC-005.

### T001 — allauth in the demo

**Files**: `pyproject.toml` (already carries `django-allauth>=65.19.4,<66` in the dev group and
the `django-mvp>=0.25.0` floor), `demo/settings.py`, `demo/urls.py`, `demo/adapter.py`,
`demo/models.py`, `demo/migrations/0001_initial.py`, `demo/management/commands/seed_demo.py`,
`tests/test_demo.py`

Research R7. `allauth` and `allauth.account` after `mvp_accounts` in `INSTALLED_APPS`, allauth's
middleware and authentication backend, console email, `allauth.urls` at `accounts/` in place of
`django.contrib.auth.urls`, `mvp.urls` included at the root. Settings: email as the sign-in
method, mandatory verification by link, sign-in by code, `"phone"` in the sign-up fields,
re-authentication required. A demo adapter storing phone numbers in a demo `PhoneNumber` model
(one-to-one to the user, `verbose_name`/`help_text` on each field) and printing SMS codes.
`seed_demo` creates a verified primary `EmailAddress` for each account, still idempotent.
`tests/factories.py` gains one factory per model the tests build: the user, allauth's
`EmailAddress` (verified and primary by default) and the demo's `PhoneNumber`. `tests/conftest.py`
gains a thin `signed_in_client` fixture over them. Later tasks use these instead of constructing
objects inline (Article X). The `PhoneNumber` number is `unique=True`.
Tests: the sign-in page responds at allauth's URL; a seeded account signs in with `password`.

### T002 — The URLconf-rebuilding fixture

**Files**: `tests/conftest.py`

Research R6. A fixture taking settings overrides, applying them, reloading `allauth.account.urls`,
`allauth.urls`, `demo.urls` and `tests.urls`, clearing URL caches, and undoing all of it on
teardown. A test proving it: with `ACCOUNT_LOGIN_BY_CODE_ENABLED=False`,
`account_request_login_code` does not resolve, and after teardown it does.

### T003 — Entrance layout

**Files**: `mvp_accounts/templates/allauth/layouts/base.html`,
`mvp_accounts/templates/allauth/layouts/entrance.html`,
`mvp_accounts/templates/account/logout.html`, `tests/test_entrance_pages.py`,
`pyproject.toml` (`non-mirror-paths`)

Research R1, R2. allauth's sign-out page extends its management base, and the spec makes it an
entrance page, so `account/logout.html` is a copy of allauth 65.19.4's page with its parent
switched to `allauth/layouts/entrance.html` and nothing else changed; a comment at its top says
so and names the allauth version it was copied from. Page tests per the plan's four assertions for sign-in, sign-up, sign-out
(signed in), request code and confirm code (after requesting one), sign-up closed (demo adapter
or an override closing sign-up), and account inactive. The title carries allauth's `head_title` on pages that do not fill their own `title` block (the
code-entry pages do, research R1).
Messages render on an entrance page. Sign-out's message appears on the page that follows.

### T004 — Elements

**Files**: `mvp_accounts/templates/allauth/elements/*.html` (R4's list),
`tests/test_elements.py`

Built from django-mvp components. Tests:
- a sign-up submitted with errors shows allauth's error for each field next to it and the
  non-field error on the page (SC-005, US1 scenario 2);
- a wrong-password sign-in shows allauth's non-field error;
- every rendered input on sign-in and sign-up has a `<label for>` matching its id, and its help
  text and errors are referenced from its `aria-describedby` by ids present on the page (FR-015).
  This is the whole-form path and must pass;
- the same assertion on a single-field input rendered through the `field` element, submitted with
  an error (the change-email form with `ACCOUNT_CHANGE_EMAIL=True`, through T002's fixture). The
  label's `for` must pass. The help-text and error association is written in full and **skipped**,
  with a reason naming django-mvp#412;
- buttons render as the theme's buttons, and a `href` button renders as a link.

### T005 — What a project turned off is not offered

**Files**: `tests/test_entrance_pages.py`

With T002's fixture: sign-in by code off → the sign-in page offers no code; sign-up closed →
the sign-up page is allauth's closed page. allauth's sign-in page still links to sign-up when
it is closed; that link is allauth's own, and the test asserts only that the package adds no
other. Closing sign-up is an adapter decision in allauth, so the test uses a test adapter whose
`is_open_for_signup` returns False, set with `override_settings(ACCOUNT_ADAPTER=...)`. (Code
reset and code verification belong to US2, phone to US3.)

### T006 — A host project's own override wins

**Files**: `tests/test_entrance_pages.py`, `tests/templates_host_override/account/login.html`

`override_settings` putting that directory in `TEMPLATES[0]["DIRS"]`. The sign-in page renders
the project's template (FR-011).

### T007 — Adoption documentation and the glossary

**Files**: `README.md`, `CHANGELOG.md`, `CONTEXT.md`

README: install the package and allauth, list `mvp_accounts` ahead of `allauth` and `mvp` in
`INSTALLED_APPS` and why, include allauth's URLs and django-mvp's, supported allauth range
65.19.4 to below 66, nothing is checked (FR-009, FR-010, SC-002). CHANGELOG `Unreleased`.
`CONTEXT.md` **Account** no longer says closing an account is provided (FR-013).

---

## US2 — Get back in after forgetting a password (P1)

Issue: #11. Delivers US2's scenarios over US1's layout, and US2's part of SC-001 and SC-004.

### T008 — Password reset by link

**Files**: `tests/test_recovery_pages.py`

Request page, "check your email" page, the new-password page reached from the emailed link
(read from `mail.outbox`), the confirmation page, and an invalid or used link. Each an entrance
page per the plan's four assertions.

### T009 — Password reset by code

**Files**: `tests/test_recovery_pages.py`

T002's fixture with `ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED=True`: the code page and the
new-password page render as entrance pages. With it off (the demo), the request page offers no
code.

### T010 — Email verification

**Files**: `mvp_accounts/templates/account/verified_email_required.html`,
`tests/test_recovery_pages.py`

allauth's "verified email required" page extends its management base, and the spec makes it an
entrance page, so the override is a copy of allauth 65.19.4's page with its parent switched to
`allauth/layouts/entrance.html`, commented as T003's sign-out copy is.

Sign-up under mandatory verification: "verification sent", the confirmation page from the emailed
link, and "verified email required" (a view decorated with allauth's `verified_email_required`,
added to `tests/urls.py`). With `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True` through the
fixture, the code page renders as an entrance page.

---

## US3 — Reach account management from anywhere on the site (P2)

Issue: #12. Delivers FR-006, FR-007, FR-008, FR-014, and US3's part of SC-003 and SC-004.

### T011 — Account Center menu entries

**Files**: `mvp_accounts/menus.py`, `mvp_accounts/apps.py`, `tests/test_menus.py`,
`tests/test_apps.py`

Research R5, R6. `ready()` imports `menus` only when `allauth.account` is installed. Entries
"Email" (`account_email`), "Password" (`account_change_password`), "Phone number"
(`account_change_phone`), labels translatable, icons `email`, `password` and `phone`, which
django-mvp's icon pack already names (no project registration needed). Tests on the rendered
Account Center page: all three entries with phone on; no phone entry with phone off (fixture).

### T012 — Account overview cards

**Files**: `mvp_accounts/templates/mvp/account/overview.html`, `tests/test_account_center.py`

Research R5. Extends `mvp/account/overview.html`, adds to `account.cards` through
`{{ block.super }}`: one card per management page (email, password, phone), each resolving its
URL with `{% url … as %}` and drawn only when it resolves. Password card links to
`account_change_password` (allauth redirects a person without a password to set one). Tests:
cards present for a signed-in person; no phone card with phone off; a template in its own
directory, `tests/templates_chained_card/mvp/account/overview.html`, put first in
`TEMPLATES[0]["DIRS"]` by `override_settings` in that one test, chains onto the same block and
shows beside this package's cards (FR-007).

### T013 — The user menu

**Files**: `tests/test_account_center.py`

Signed in: the shell's user menu links to the Account Center and its sign-out form posts to
allauth's `account_logout`. Signed out: neither entry is on the page.

### T014 — Without allauth

**Files**: `tests/settings_without_allauth.py`, `tests/test_without_allauth.py`,
`pyproject.toml` (`non-mirror-paths`)

Research R8. A subprocess under the no-allauth settings: the package imports, the menus build,
the demo overview and the Account Center render with 200, and `AccountCenterMenu` holds none of
this package's entries.

### T015 — Translation catalogue

**Files**: `mvp_accounts/locale/en/LC_MESSAGES/django.po`

`makemessages -l en` from inside `mvp_accounts/`. Every string T011 and T012 add appears in it.

---

## US4 — Change email addresses, password and phone number (P2)

Issue: #13. Delivers FR-003 and US4's scenarios.

### T016 — Management layout

**Files**: `mvp_accounts/templates/allauth/layouts/manage.html`,
`mvp_accounts/templates/account/base_entrance.html`, `tests/test_management_pages.py`

Research R3, and R1's *Four pages*. `manage.html` extends `mvp/account/base.html` and maps
allauth's blocks. `account/base_entrance.html` extends
`user.is_authenticated|yesno:"allauth/layouts/manage.html,allauth/layouts/entrance.html"`, so
re-authentication and phone verification after a change render as management pages, while the
same code page during sign-up stays an entrance page (assert both). The email page is claimed
by the Account Center, so its sidebar draws `AccountCenterMenu` (moved here from T011).
Navigation is asserted by the sidebar's navigation menu, not by a label (plan, *What every page
test asserts*). Page tests (shell and its
navigation present, bare layout absent, allauth's form present) for: email with several
addresses (verified and primary shown, allauth's actions present); change email with
`ACCOUNT_CHANGE_EMAIL=True` through the fixture; password change; password set for an account
with no usable password; phone change and phone verification by code; re-authentication. A test
that the page body sits inside the Account Center layout's container, **skipped** with a reason
naming django-mvp#358.

### T017 — Warn-no-email snippet

**Files**: `tests/test_management_pages.py`

The email page for an account with no address renders allauth's warning inside the shell. Override
`account/snippets/warn_no_email.html` only if the warning renders unstyled with the elements
alone.
