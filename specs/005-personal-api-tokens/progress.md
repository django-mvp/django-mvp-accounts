# Progress — 005 Personal API tokens

## 2026-10-08T09:36:36Z · Plan · T001

Did: research, plan and tasks written from the approved prototype. Ledger created.
Verified: prototype pages walked on the demo before approval. No tests yet.
Next: design review, then T001.
Watch: the approved templates keep their markup and words.

## 2026-10-08T09:51:17Z · Implementer US1 · T002

Did: raised the api extra's Django REST framework bound to >=3.16,<4 and re-locked (uv lock, uv sync). Added TestApiExtra (bounds of both requirements, neither a runtime dependency) and TestDemoApiTokens (knox's token model installed, makemigrations --check clean) to tests/test_demo.py.
Verified: `uv run pytest tests/test_demo.py::TestApiExtra tests/test_demo.py::TestDemoApiTokens -q` 5 passed. Red step: the DRF bound test failed first (3.15.2 still allowed); the knox-installed and no-migration tests passed on first run because T001 kept knox in the demo, so they pin an existing state rather than driving a change. pre-commit run --all-files passed.
Next: T003, AuthTokenFactory.
Watch: knox's bound was already >=5.0,<6 in the extra.

## 2026-10-08T09:52:10Z · Implementer US1 · T003

Did: added AuthTokenFactory to tests/factories.py (built through knox's manager, complete value kept on `token`, `expiry` and `created` overridable and written by update), an `auth_token` fixture in tests/conftest.py, and tests/test_factories.py::TestAuthTokenFactory.
Verified: `uv run pytest tests/test_factories.py -q` 10 passed. Red step: collection failed with ImportError for AuthTokenFactory before the factory existed. pre-commit run --all-files passed.
Next: T004, routes and the tokens page.
Watch: `expiry` on the factory is an absolute moment (or None), not knox's timedelta, so a test can make an expired token directly.

## 2026-10-08T09:55:09Z · Implementer US1 · T004

Did: added mvp_accounts/tokens/urls.py (three routes, the revoke one on a path converter) and views.py (TokenPageMixin on UserPassesTestMixin, test_func asks only is_authenticated, get_working_tokens(); TokensView, CreateTokenView, RevokeTokenView), included the routes in demo/urls.py at account/tokens/ ahead of mvp.urls, changed list.html's two digest expressions to token_key, removed django-rest-knox from the deptry DEP002 ignore list. Ran migrate and seed_demo after the route change.
Verified: `uv run pytest tests/test_tokens -q` 24 passed. Red step: collection failed with ImportError for the views before they existed, then the visitor tests failed on a fixture mistake of mine (fixed in the test). Mutation probes, each reverted: test_func returning True fails the three visitor tests; list.html back to token.digest fails the revoke-link test; dropping get_working_tokens() from the revoke lookup fails the stranger and expired tests. pre-commit run --all-files passed; deptry passes with knox off the ignore list.
Next: T005, the API tokens entry.
Watch: see decisions.md D21. TokensView already supplies `tokens`, so some of T009's row tests will pass before US3 writes any code.
