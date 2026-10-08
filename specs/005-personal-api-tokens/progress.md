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

## 2026-10-08T09:56:55Z · Implementer US1 · T005

Did: mvp_accounts/menus.py now appends the "Account" group whether or not allauth is installed: allauth's entries and the reauthentication pages only when it is, the api_tokens entry (pages: create and revoke routes, no check) always, last. Added tests/urls_without_knox.py (demo routes without the tokens include, not importing demo.urls); tests/urls_without_allauth.py gained the tokens include. New TestApiTokensEntry in tests/test_menus.py. Updated the two tests that pinned the old group: tests/test_apps.py (children list gains api_tokens) and tests/test_without_allauth.py (the "no account group without allauth" assertion became "the group holds only api_tokens"; the script now also requests the tokens page; two new tests for the entry and the 200).
Verified: `uv run pytest tests/test_apps.py tests/test_menus.py tests/test_without_allauth.py tests/test_tokens -q` 44 passed. Against the previous menus.py, the new and updated tests fail (5 failed, 6 errors in the subprocess module). Probes: pointing the no-tokens test at tests.urls fails it; removing the tokens include from urls_without_allauth.py errors the subprocess module. pre-commit passed.
Next: T006, the landing page card.
Watch: the two pre-existing tests above were changed as the brief sanctions.

## 2026-10-08T09:58:55Z · Implementer US1 · T006

Did: added the API tokens card after Sessions in mvp_accounts/templates/mvp/account/overview.html, behind `{% url "account_api_tokens" as tokens_url %}`, with the words and icon of the prototype (8e708c7). Tests: API tokens added to the CARDS table in tests/test_account_center.py; a test that with tests.urls_without_knox the card count drops by one and no card links to the tokens page; a test in tests/test_without_allauth.py that the card's link is in the cards of the run without allauth.
Verified: `uv run pytest tests/test_account_center.py tests/test_without_allauth.py -q` 21 passed. Red step: the CARDS case and the no-allauth card test failed before the template change. Probe, reverted: replacing the guard with `{% if True %}` fails the no-tokens test (a first version of that test, which counted links, did not catch it because an empty href renders no anchor; it now counts the cards in the grid). pre-commit passed.
Next: T007, without knox and without Django REST framework.
Watch: none.

## 2026-10-08T10:00:12Z · Implementer US1 · T007

Did: tests/settings_without_knox.py (the suite's settings without the knox and rest_framework apps and without REST_FRAMEWORK and REST_KNOX, routed by tests.urls_without_knox) and tests/test_without_knox.py: one subprocess run with sys.modules["knox"] and sys.modules["rest_framework"] set to None before django.setup(). It asserts the package is installed and neither app is, the tokens route does not reverse, no knox.* or rest_framework.* module is loaded, the landing page and the Account Center answer 200, and the Account Center has no link to the tokens page. Declared the module in pyproject.toml non-mirror-paths.
Verified: `uv run pytest tests/test_without_knox.py -q` 5 passed. Red step: the run failed while the settings module did not exist; once it did, the tests passed on first run because T005 and T006 had already built the behaviour. So probes, each reverted: `import knox` at the top of mvp_accounts/menus.py makes every test in the module error; pointing the settings at urls_without_allauth (which includes the tokens pages) does the same. pre-commit passed.
Next: T008, the decision record and documentation.
Watch: none.

## 2026-10-08T10:02:42Z · Implementer US1 · T008

Did: ADR 0005 (the package provides the API tokens pages itself) in the shape of ADR 0002; docs/adr/README.md gained a Records list naming all five; ADR 0002 gained one sentence pointing at ADR 0005 where it says the menu adds nothing without allauth; README gained an "API tokens" section (the extra, knox and Django REST framework in INSTALLED_APPS and migrate, the tokens include, knox's authentication class in the project's own settings, that none of it is checked, the three views and the mixin by name) and API tokens in the Account Center list, with the sentence about no allauth corrected; CONTEXT.md's API token entry corrected; CHANGELOG Added entry. Nothing on creating, lifetimes, revoking or the access setting in the README.
Verified: `forge conformance --repo . --base b34bd5b` clean; `forge docs-check --repo . --base b34bd5b` first reported six undocumented public names (the three views, the mixin, and two working names in menus.py), fixed by documenting the views and moving the menu's working names into the allauth branch (separate commit, T005); then clean. pre-commit run --all-files passed; the menu, apps and no-allauth tests pass (21).
Next: the full suite and lint, then the report.
Watch: the CHANGELOG entry and CONTEXT.md describe the whole feature (creating, choosing an expiry), which later stories build; the README does not.

## 2026-10-08T10:09:20Z · Implementer US3 · T009

Did: wrote TestTokensList (9 tests) in tests/test_tokens/test_views.py; added TokenPageMixin.is_at_limit() and put token_limit and at_limit in TokensView's context.
Verified: uv run pytest tests/test_tokens/test_views.py -> 26 passed. Red first: 3 failed (token_limit missing from context, create link still shown at the limit); the other 6 passed first time because US1 already supplied `tokens`. Probed each by mutation and restored: dropping the user filter fails the other-person test, dropping the expiry filter fails the expired test, a per-row user lookup fails the query-count test, an always-present <time> fails the no-expiry test, an always-present table fails the no-tokens test, expiry showing the created day fails the three-rows test, and removing the create href fails the no-tokens link check. uv run pre-commit run --all-files passed.
Next: T010, seeded tokens in seed_demo.
Watch: the query-count test makes one request before measuring, because a client's first request also records its session and costs two more queries.

## 2026-10-08T10:12:37Z · Implementer US3 · T010

Did: added TestSeededApiTokens (5 tests) to tests/test_demo.py; seed_demo now seeds staff.user with three working tokens (one with no expiry) and one expired, super.user with TOKEN_LIMIT_PER_USER tokens, regular.user with none, deleting those accounts' tokens first. The module docstring and closing output say who holds what.
Verified: uv run pytest tests/test_demo.py -> 48 passed. Red first: the tests failed with 0 tokens before the command seeded any. Probed by mutation and restored: no delete fails all 5, dropping the expired token fails 2, limit+1 fails 2, staff tokens all with an expiry fails 1, a token seeded for regular fails 1. Ran uv run python manage.py migrate (nothing to apply) and seed_demo twice; the demo database now holds 4 tokens for staff and 5 for super. uv run pre-commit run --all-files passed.
Next: full suite, report, ledger.
Watch: STAFF_TOKENS is a module constant in seed_demo.py, like OTHER_BROWSERS.

## 2026-10-08T10:16:30Z · Implementer US2 · T011

Did: tests/test_tokens/test_forms.py (TestCreateTokenForm, 8 tests) and mvp_accounts/tokens/forms.py: CreateTokenForm with one required radio choice, lifetime (7d, 30d, 90d, 1y, never), 30d initial, and get_expiry() returning a timedelta or None. The module imports nothing from knox.
Verified: `uv run pytest tests/test_tokens/test_forms.py -x` failed at collection first (no module mvp_accounts.tokens.forms), then 8 passed. Refusals are asserted by field and code (invalid_choice, required). `uv run pre-commit run --all-files` passed.
Next: T012, the create page.
Watch: 1 year is 365 days, the same as knox's timedelta addition; no leap-year logic.

## 2026-10-08T10:17:51Z · Implementer US2 · T012

Did: CreateTokenView now uses CreateTokenForm, accepts POST, and in form_valid creates the person's token through get_token_model().objects.create(user=..., expiry=form.get_expiry()); get_success_url is always the tokens page. Seven tests added to TestCreateTokenView (lifetime field present with the five choices, GET creates nothing, valid POST makes one token for the person expiring 90 days out and redirects to the tokens page, never stores no expiry, invalid choice creates nothing and shows the form with the error on lifetime, ?next= and a posted next are ignored, a visitor's POST creates nothing and is sent to sign in).
Verified: `uv run pytest tests/test_tokens/test_views.py::TestCreateTokenView` red first (4 failed: the POST answered 405); then 8 passed; `uv run pytest tests/test_tokens -q` 48 passed. The visitor test passed first time because TokenPageMixin already guards dispatch; probed by mutation and restored: test_func returning True fails it. Also: success URL taken from POST next fails the ignored-next test; expiry=None fails the 90-day test. pre-commit passed after ruff-format reflowed one test.
Next: T013, the token shown once.
Watch: none.

## 2026-10-08T10:22:47Z · Implementer US2 · T013

Did: CreateTokenView.form_valid sets the signed cookie mvp_accounts_new_token on the redirect (salt of the package's own, max_age 60, httponly, samesite Strict, secure when the request is, path the tokens page). TokensView is never_cache, reads the cookie with get_signed_cookie (same max_age), puts new_token (value and token_key) in the context only when its first TOKEN_KEY_LENGTH characters are the token_key of one of the signed-in person's working tokens, adds header_prefix, and deletes the cookie with the same path and samesite on every response of its get. tests/test_components/test_token_created.py (3 tests) and TestNewTokenShownOnce (13 tests); tests/test_components/ declared in pyproject non-mirror-paths.
Verified: `uv run pytest tests/test_tokens/test_views.py::TestNewTokenShownOnce` red first (12 failed: no cookie, no new_token or header_prefix in the context, no Cache-Control); then 61 passed in tests/test_tokens, and tests/test_tokens tests/test_components tests/test_app.py all green. The shown value is checked as the complete token by hashing it with knox's hash_token and comparing it with the stored digest. The two component tests and the escaping test passed first time because the approved component already existed; probed by mutation and restored: renaming the id, dropping the prefix from the example, and |safe on the value each fail one. View probes, each restored: httponly False, samesite Lax, path "/" on set, max_age 3600 on set, set_cookie in place of delete_cookie, delete without path, no never_cache, no ownership match, no max_age on read, unsigned read, the value put in the session, and a token created by GET each fail at least one test. pre-commit passed.
Next: T014, the limit.
Watch: the cookie is deleted on every GET of the tokens page, with or without one sent, as the brief says; ruff S105 matches names containing TOKEN, so the constants are SHOWN_ONCE_COOKIE, _SALT and _MAX_AGE. knox.create returns (record, value); the view takes index 1 because ruff RUF059 rejects an unused unpacked name and underscore names are banned.

## 2026-10-08T10:26:03Z · Implementer US2 · T014

Did: CreateTokenView.get and .post check TokenPageMixin.is_at_limit() and, at the limit, call refuse_at_limit(): messages.error and a redirect to the tokens page. Added TestCreateTokenAtTheLimit (7 tests): GET and POST at the limit create nothing, add one error-level message and redirect to the tokens page; the page it returns to has no link to the create page; an expired token does not count; a token with no expiry does; another person's tokens do not count; with no limit set creating is never refused.
Verified: `uv run pytest tests/test_tokens/test_views.py::TestCreateTokenAtTheLimit` red first (3 failed: GET answered 200, POST and the no-expiry case created a token); then `uv run pytest tests/test_tokens -q` 68 passed. The no-link test first passed for the wrong reason (the create page was not redirected, so it looked at the create page); I added an assertion that the redirect chain ends at the tokens page, and it failed with the GET check removed. The expired, other-person and no-limit tests passed first time, because the guard did not exist yet to over-refuse; probed by mutation and restored: counting all of the person's tokens fails the expired test, counting everyone's fails the other-person test, is_at_limit true when no limit is set fails the no-limit test, dropping no-expiry tokens from the working set fails the no-expiry test, removing the GET check or the POST check fails their tests, messages.info fails the level test. pre-commit passed.
Next: T015, a real request to the demo's API.
Watch: the limit tests set REST_KNOX through pytest-django's settings fixture, which is the same setting_changed route as override_settings.

## 2026-10-08T10:27:35Z · Implementer US2 · T015

Did: demo/api.py holds WhoAmIView (IsAuthenticated, returns the request user's email), routed in demo/urls.py at api/whoami/ as api-whoami. demo/views.py and tests/urls_without_knox.py do not import it. TestDemoWhoAmI (2 tests) in tests/test_demo.py: a token made through the create page and sent as `Authorization: <AUTH_HEADER_PREFIX> <value>` from a client with no session is answered with that person's email; a request with no token gets 401.
Verified: `uv run pytest tests/test_demo.py::TestDemoWhoAmI` red first (NoReverseMatch for api-whoami), then 2 passed; `uv run pytest tests/test_demo.py tests/test_without_knox.py -q` 55 passed. Probed by mutation and restored: permission_classes empty fails the no-token test, a fixed email fails the token test, authentication_classes empty fails both. pre-commit passed. Ran `uv run python manage.py migrate` (nothing to apply) and seed_demo.
Next: T016, the README and CHANGELOG.
Watch: none.

## 2026-10-08T10:28:11Z · Implementer US2 · T016

Did: README "Creating a token" under "API tokens": the five lifetimes and 30 days selected, CreateTokenForm named, shown once and what to do if a token is lost, the signed cookie that carries it, no name and no last-used time, TOKEN_TTL reaching only knox's own views, TOKEN_LIMIT_PER_USER honoured by the pages with how expired and no-expiry tokens count, that knox sets no limit so a project should set one (with the setting), the Authorization header and AUTH_HEADER_PREFIX, the demo's /api/whoami/. CHANGELOG: the one Added entry US1 wrote now also says what creating does; no second entry. No other page under docs/ describes anything this story changed (ADR 0005 and the roadmap speak of "a page to create one" and stay true).
Verified: `forge docs-check --repo . --base 906f348` first reported CreateTokenForm undocumented; after naming it in the README it is clean. `forge conformance --repo . --base 906f348` clean. pre-commit passed.
Next: the full suite and lint once, the report and the ledger.
Watch: the README says a person who loses a token revokes it and creates another, which the list page already says; the revoke action itself is a later story.

## 2026-10-08T10:34:12Z · Implementer US4 · T017

Did: RevokeTokenView.get/post redirect with a warning for a key that is unknown, expired or another person's (one refuse_gone response); GET renders the confirmation for the named working token and deletes nothing. Replaced the Http404 in get_token with None. POST for a held token is a temporary 405 until T018.
Verified: `uv run pytest tests/test_tokens/test_views.py -q` -> 65 passed. Gone-token tests were red first (KeyError 'location': the view raised 404). Passed first time, probed by mutation: loading deletes nothing (GET made to delete -> 3 tests failed), the lookup scoping (unscoped lookup -> 8 failed), the indistinguishable response (key echoed in message -> 2 failed), the list row link (href changed -> test_a_row_links_to_the_revoke_page_by_token_key failed). Mutations reverted.
Next: T018, POST deletes the one record.
Watch: the earlier tests asserted `status_code != 200` rather than 404, so none needed changing.

## 2026-10-08T10:35:34Z · Implementer US4 · T018

Did: RevokeTokenView.post deletes the one record found (token.delete(), not a queryset delete), adds messages.success and redirects to the tokens page. Replaced the temporary 405 from T017. Tests in TestRevokingAToken (tests/test_tokens/test_views.py) and TestDemoRevokedToken (tests/test_demo.py, real requests to api-whoami).
Verified: `uv run pytest tests/test_tokens/test_views.py tests/test_demo.py::TestDemoRevokedToken -q` -> 72 passed. Red first: 5 of 7 new tests failed (405, token not deleted, revoked token still answered 200). The stranger and visitor POST tests passed first time (the T017 redirect and the mixin already did it), so probed by mutation: unscoped lookup failed the stranger test; test_func returning True failed the visitor test; queryset delete over the filter failed the shared-key test; a no-op delete failed 4 tests including the demo one. Mutations reverted.
Next: T019, README and CHANGELOG.
Watch: none.
