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
