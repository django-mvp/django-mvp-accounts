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
