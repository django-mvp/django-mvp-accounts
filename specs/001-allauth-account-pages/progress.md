# Progress — 001 Accounts, sign-in and recovery on the site's own pages

- 2026-09-26 — Planning started on a fresh branch off main (132d691). Base suite green: 10 passed. django-mvp floor raised to 0.25.0 and django-allauth 65.19.4 added to the development group.

## 2026-09-26T09:20Z · Implementer US1 · T001
Did: the demo runs allauth (apps, middleware, backend, console email, `allauth.urls` at `accounts/`, `mvp.urls` at the root, the settings T001 names), a demo adapter storing phone numbers in a demo `PhoneNumber` model with its migration, `seed_demo` creating verified primary addresses, one factory per model and a `signed_in_client` fixture.
Verified: `uv run pytest tests/test_demo.py tests/test_app.py` — 13 passed; `uv run pre-commit run --all-files` — all hooks pass. The new tests failed at collection before allauth was installed in the demo.
Next: T002.
Watch: the demo's seed tests set `settings.DEBUG = True` because `seed_demo` refuses to run otherwise.
