# Progress — 001 Accounts, sign-in and recovery on the site's own pages

- 2026-09-26 — Planning started on a fresh branch off main (132d691). Base suite green: 10 passed. django-mvp floor raised to 0.25.0 and django-allauth 65.19.4 added to the development group.

## 2026-09-26T09:20Z · Implementer US1 · T001
Did: the demo runs allauth (apps, middleware, backend, console email, `allauth.urls` at `accounts/`, `mvp.urls` at the root, the settings T001 names), a demo adapter storing phone numbers in a demo `PhoneNumber` model with its migration, `seed_demo` creating verified primary addresses, one factory per model and a `signed_in_client` fixture.
Verified: `uv run pytest tests/test_demo.py tests/test_app.py` — 13 passed; `uv run pre-commit run --all-files` — all hooks pass. The new tests failed at collection before allauth was installed in the demo.
Next: T002.
Watch: the demo's seed tests set `settings.DEBUG = True` because `seed_demo` refuses to run otherwise.

## 2026-09-26T09:30Z · Implementer US1 · T002
Did: `rebuild_urls` fixture in `tests/conftest.py`, a context manager that applies settings overrides, reloads allauth's, the demo's and the suite's URLconfs, and reloads them again from the restored settings on the way out.
Verified: `uv run pytest tests/test_demo.py` — 9 passed. With `ACCOUNT_LOGIN_BY_CODE_ENABLED=False` the code route does not resolve, and it resolves again afterwards. The tests failed on the missing fixture first.
Next: T003.
Watch: it is used as `with rebuild_urls(...):`, so the restore happens at the end of the block, not at test teardown.

## 2026-09-26T09:50Z · Implementer US1 · T003
Did: the entrance layout (`allauth/layouts/entrance.html` on django-mvp's entrance page, messages drawn above a medium card), the base layout that falls through to it, and `account/logout.html` as a copy of allauth 65.19.4's page with its parent switched. Page tests for sign-in, sign-up, sign-out, request and confirm code, sign-up closed and account inactive, plus messages on an entrance page and after sign-out. `tests/test_entrance_pages.py` is declared in `non-mirror-paths`.
Verified: `uv run pytest tests/test_entrance_pages.py` — 9 passed; eight failed against allauth's bare layout first. Removing the messages line or the title mapping makes the tests fail.
Next: T004.
Watch: `tests/adapters.py` holds the closed-sign-up adapter T005 uses.

## 2026-09-26T10:25Z · Implementer US1 · T004
Did: the twelve elements (alert, badge, button, button_group, details, field, fields, form, h1, h2, hr, p) built from django-mvp components; `tests/test_elements.py`, declared in `non-mirror-paths`. `rebuild_urls` now also reloads `allauth.account.views`.
Verified: `uv run pytest tests/test_elements.py tests/test_demo.py` — 26 passed, 1 skipped (the single-field help-text and error association, django-mvp#412; with the skip removed it fails on the missing `aria-describedby`, as the issue describes). 12 tests failed against allauth's bare elements first. Swapping `fields` for a plain `as_div` render fails the field-error test.
Next: T005.
Watch: the failed-sign-up test covers field errors only. Nothing in the demo's sign-up produces a non-field error, and the wrong-password sign-in covers allauth's non-field error.

## 2026-09-26T10:40Z · Implementer US1 · T005
Did: tests that a project's choices show on the sign-in page: an emailed-code option only while `ACCOUNT_LOGIN_BY_CODE_ENABLED` is on (through `rebuild_urls`), and, with the closed-sign-up adapter, allauth's one sign-up link and nothing added beside it, ending on the closed page.
Verified: `uv run pytest tests/test_entrance_pages.py` — 12 passed. The behaviour is allauth's and the tests passed on first run, so each was probed by adding a hard-coded link to the entrance layout: the code test and the link-count test then fail.
Next: T006.
Watch: none.

## 2026-09-26T10:45Z · Implementer US1 · T006
Did: `tests/templates_host_override/account/login.html` and a test that, with that directory first in `TEMPLATES[0]["DIRS"]`, the sign-in page is the project's own.
Verified: `uv run pytest tests/test_entrance_pages.py` — 13 passed. Without the settings change the same test fails, so the directory is what puts the page there.
Next: T007.
Watch: none.

## 2026-09-26T10:55Z · Implementer US1 · T007
Did: README installation section (install both packages, the supported allauth range, `mvp_accounts` ahead of `allauth` and `mvp` and why, both URL includes, nothing checked or configured); CHANGELOG entries under Unreleased; `CONTEXT.md` **Account** no longer says closing an account is provided. There is no `docs/` page describing this behaviour, so none changed.
Verified: `uv run pre-commit run --all-files` — all hooks pass.
Next: full verify, then the report.
Watch: the README's scope section still names the package it supersedes, a line that was on main before this story.

## 2026-09-26T11:20Z · Implementer US2 · T008
Did: `tests/test_recovery_pages.py` with `TestPasswordResetByLink`: request page, "check your email", new-password page from the emailed link, "password changed", an invalid link and a used link, each through the four entrance-page assertions. Added the module to `non-mirror-paths`.
Verified: `uv run pytest tests/test_recovery_pages.py` — 6 passed. Probed by pointing the entrance layout at allauth's bare base: all six fail.
Next: T009.
Watch: none.

## 2026-09-26T11:25Z · Implementer US2 · T009
Did: `TestPasswordResetByCode`: with `ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED=True` through `rebuild_urls`, the code page and the new-password page (code read from `mail.outbox`) are entrance pages; with it off, the request page has no word "code".
Verified: `uv run pytest tests/test_recovery_pages.py::TestPasswordResetByCode` — 3 passed.
Next: T010.
Watch: the "no code" test only fails if a page adds the word; allauth's request page is identical with the setting on, so it guards the package's own markup rather than allauth's.

## 2026-09-26T11:35Z · Implementer US2 · T010
Did: `account/verified_email_required.html` (copy of allauth 65.19.4's with its parent switched to the entrance layout), `members_only` test view in `tests/urls.py`, and `TestEmailVerification`: "verification sent", the confirmation page from the emailed link, "verified email required" for a signed-in person with an unverified address, and the code page under `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED`. CHANGELOG entry.
Verified: `uv run pytest tests/test_recovery_pages.py` — 13 passed. The verified-email-required test passed before the override existed (see decisions).
Next: full verify, then the report.
Watch: allauth rate-limits confirmation mail per address in the cache, which outlives a test; each sign-up test uses its own address.

## 2026-09-26T11:20Z · Implementer US3 · T011
Did: `mvp_accounts/menus.py` appends Email, Password and Phone number entries to django-mvp's Account Center menu; `MvpAccountsConfig.ready()` imports it only when `allauth.account` is installed. `tests/test_menus.py` and `tests/test_apps.py` assert on the rendered Account Center page (links, labels, icons; no phone entry with phone off). deptry ignore for `flex_menu` (a transitive dependency through django-mvp) in `pyproject.toml`.
Verified: `uv run pytest tests/test_menus.py tests/test_apps.py` — 12 passed; the first test failed before the module existed. `uv run pre-commit run --all-files` — all hooks pass.
Next: T012.
Watch: the phone entry is dropped by django-mvp because its URL does not resolve, so nothing in menus.py checks the setting.

## 2026-09-26T11:35Z · Implementer US3 · T012
Did: `mvp_accounts/templates/mvp/account/overview.html` extends the same-named django-mvp template and adds an Email, Password and Phone number card after `{{ block.super }}`, each behind `{% url ... as %}`. `tests/test_account_center.py` (`TestOverviewCards`, `TestChainedCard`) with the chained template in `tests/templates_chained_card/`; the module is in `non-mirror-paths`.
Verified: `uv run pytest tests/test_account_center.py` — 9 passed; the five card tests failed before the template existed.
Next: T013 (tests only).
Watch: none.

## 2026-09-26T11:36Z · Implementer US3 · T013
Did: `TestUserMenu` in `tests/test_account_center.py`: signed in, the overview page's user menu links to the Account Center and holds a form posting to `account_logout`; signed out, neither.
Verified: `uv run pytest tests/test_account_center.py::TestUserMenu` — 3 passed. These pass on first run because the behaviour is django-mvp's; probed by making its user menu template draw nothing, which fails the two signed-in tests.
Next: T014.
Watch: the tests read the demo overview page, not the Account Center: the Account Center swaps the user menu's own Account Center row for its sidebar navigation (see decisions).

## 2026-09-26T11:50Z · Implementer US3 · T014
Did: `tests/settings_without_allauth.py`, `tests/urls_without_allauth.py` and `tests/test_without_allauth.py`, which start Django in a subprocess without allauth's apps, middleware, backend, adapter or routes, then render the demo overview and the Account Center for a signed-in person. The guard moved into `menus.py` and `ready()` was dropped (see decisions); `tests/test_apps.py` follows.
Verified: `uv run pytest tests/test_without_allauth.py tests/test_apps.py tests/test_menus.py` — 16 passed. The subprocess test failed first with the import guarded only in `ready()`: the entries were on the menu and the page raised.
Next: T015.
Watch: none.

## 2026-09-26T11:55Z · Implementer US3 · T015
Did: `mvp_accounts/locale/en/LC_MESSAGES/django.po` from `makemessages -l en` run inside `mvp_accounts/`; it holds the labels and card texts from `menus.py` and the overview template.
Verified: grepped the catalogue for each of the nine strings T011 and T012 added: all present. It also holds the strings from earlier stories' templates, which the command picks up.
Next: README, CHANGELOG, full verify, report.
Watch: the catalogue has empty `msgstr`s, which is what a base English catalogue is.

## 2026-09-26T12:20Z · Implementer US4 · T016
Did: `allauth/layouts/manage.html` extends `mvp/account/base.html` and maps allauth's four blocks; `account/base_entrance.html` extends the management layout for a signed-in person and the entrance layout otherwise. `tests/test_management_pages.py` (in `non-mirror-paths`) asserts stylesheet, sidebar navigation menu, no bare `Menu:` list and the page's own form for email (three addresses), change email, password change, password set, phone change, phone verification by code (code read from the demo adapter's printed line), re-authentication; the email, password and phone pages draw "Account navigation"; a message allauth adds shows in the shell; phone verification during sign-up is an entrance page. The container test is skipped naming django-mvp#358. README and CHANGELOG say management pages render in the Account Center.
Verified: `uv run pytest tests/test_management_pages.py` — 10 passed, 1 skipped (django-mvp#358); the management tests failed first (no sidebar menu on any page). Probed the base override: making it always entrance fails the phone verification and re-authentication tests, always management fails the sign-up test. `tests/test_entrance_pages.py` and `tests/test_recovery_pages.py` stay green (sign-out and "verified email required" remain entrance pages while signed in). `uv run pre-commit run --all-files` — all hooks pass.
Next: T017.
Watch: allauth rate-limits phone codes per address and IP in the cache, so the module clears the cache before each test.

## 2026-09-26T12:30Z · Implementer US4 · T017
Did: `account/snippets/warn_no_email.html` draws allauth's warning through the `alert` element (warning variant). `TestWarnNoEmail` opens the email page for an account with no address.
Verified: `uv run pytest tests/test_management_pages.py::TestWarnNoEmail` — failed first (the warning was a bare paragraph), passes now. `uv run pre-commit run --all-files` — all hooks pass.
Next: full verify, report.
Watch: the account needs a blank `email` on the user, or allauth's email page creates an address from it before drawing the warning.
