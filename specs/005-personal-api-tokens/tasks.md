# Tasks — 005 Personal API tokens

**Branch**: `005-personal-api-tokens` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it.

The approved templates are kept: `mvp_accounts/templates/mvp_accounts/tokens/list.html`,
`create.html`, `revoke.html` and `mvp_accounts/templates/cotton/mvp_accounts/token/created.html`.
A task changes one only where it says so, and never its words or layout.

No test asserts wording, a CSS class or an icon. Rows are found by `token_key`, forms by field
name, messages by level, links by `href`.

## Order

**Foundational → US1 → US3 → US2 → US4 → US5, one at a time, in one working tree** (plan, *Story
order*).

---

## Foundational

### T001 — Remove the prototype's Python

**Files**: `mvp_accounts/tokens/access.py`, `forms.py`, `urls.py`, `views.py`,
`mvp_accounts/templatetags/`, `mvp_accounts/menus.py`,
`mvp_accounts/templates/mvp/account/overview.html`, `demo/access.py`, `demo/settings.py`,
`demo/urls.py`, `demo/views.py`, `demo/management/commands/seed_demo.py`, `tests/test_app.py`

Delete the four modules under `mvp_accounts/tokens/` (keep its `__init__.py`), the template tag
package, `demo/access.py`, the demo's API view and both of its token routes, the seed command's
token seeding and the `MVP_ACCOUNTS_API_TOKEN_ACCESS` line. Put `mvp_accounts/menus.py` and the
landing page template back as they are on `main`. Keep the four approved templates, the `api`
extra, and Django REST framework and knox in the demo's installed apps with their settings.
`tests/test_app.py` pins the list of this package's components: add `created.html`, which stays on
disk. The suite is green afterwards and every later task starts red.

---

## US1 — A developer turns on API tokens for a project (P1)

Issue: #37. Delivers FR-002 to FR-005, FR-012, FR-014, US1's part of FR-001, FR-006, FR-015,
FR-016 and FR-017, and SC-005.

### T002 — The install extra and the demo's apps

**Files**: `pyproject.toml`, `uv.lock`, `tests/test_demo.py`

Research R8. The `api` extra reads `djangorestframework>=3.16,<4` and `django-rest-knox>=5.0,<6`,
and neither is in `[project] dependencies`. Tests: knox's token model is installed in the demo and
`makemigrations --check` is clean (the package adds no migration, FR-012).

### T003 — A factory for knox's token

**Files**: `tests/factories.py`, `tests/conftest.py`

Research R9. `AuthTokenFactory` builds a token through knox's manager for a user from the existing
user factory, with `expiry` and `created` overridable, and keeps the complete value on the
instance it returns so a test can send it. One factory, variants at the call site. `created` is
`auto_now_add` on knox's model, so an override is written with an update after knox's manager
returns.

### T004 — The routes and the tokens page

**Files**: `mvp_accounts/tokens/urls.py`, `mvp_accounts/tokens/views.py`,
`mvp_accounts/templates/mvp_accounts/tokens/list.html`, `demo/urls.py`,
`tests/test_tokens/__init__.py`, `tests/test_tokens/test_urls.py`,
`tests/test_tokens/test_views.py`

Plan *Routes*, *Views*. All three routes of plan *Routes* are registered here, because the
approved list template reverses the create and revoke routes for every person and every row. The
demo includes `mvp_accounts.tokens.urls` at `account/tokens/`, ahead of django-mvp's routes.
`test_urls.py` asserts all three names reverse. `TokenPageMixin` is introduced here with
`test_func` asking only whether the person is signed in, and with `get_working_tokens()` using the
filter research R1 gives. `TokensView`, `CreateTokenView` and `RevokeTokenView` each render their
approved template inside the Account Center for a signed-in person and send anyone else to sign in
(acceptance scenario 6, FR-006). The list template's two expressions that read `digest` change to
`token_key` here, so the page renders with tokens present. What the pages do beyond rendering is
built in US3, US2 and US4.

### T005 — The API tokens entry

**Files**: `mvp_accounts/menus.py`, `tests/test_menus.py`, `tests/test_apps.py`,
`tests/test_without_allauth.py`, `tests/urls_without_allauth.py`, `tests/urls_without_knox.py`

Research R6. One more child of the "Account" group, after Sessions: `view_name`
`account_api_tokens`, `pages` naming the create and revoke routes. The group is appended whether
or not allauth is installed, holding allauth's entries only when it is. Tests: the rendered Account
Center has the entry (scenario 1). With the tokens URLs not included it has none (scenario 4):
`tests/urls_without_knox.py` is created here, the demo's routes without the tokens include and
without the demo's API, and the test runs under it. Without allauth and with the tokens URLs
included, the entry is there and the tokens page answers 200 to a signed-in person (scenario 5):
the subprocess run's routes gain the tokens include and its script requests the page. Update the two tests that pin
the group's children and its absence without allauth to what is now true.

### T006 — The API tokens card

**Files**: `mvp_accounts/templates/mvp/account/overview.html`, `tests/test_account_center.py`,
`tests/test_without_allauth.py`

One card after Sessions, behind `{% url "account_api_tokens" as tokens_url %}`, with the words
and icon the prototype had (commit `8e708c7`). Tests: add it to the module's `CARDS` table, assert
no card when the tokens URLs are not included (scenario 4), and assert the card's link to the
tokens page is in the Account Center the run without allauth returns (scenario 5, FR-005).

### T007 — Without knox, and without Django REST framework

**Files**: `tests/settings_without_knox.py`, `tests/test_without_knox.py`, `pyproject.toml`
(`non-mirror-paths`)

Research R6. Settings from the suite's with `knox` and `rest_framework` out of the installed apps
and their settings removed, routed by `tests/urls_without_knox.py` (T005). One subprocess run
through `run_in_subprocess`, with `sys.modules["knox"]` and `sys.modules["rest_framework"]` set to
`None` before `django.setup()`. It asserts the package imports, the Account Center and its landing
page answer 200, there is no tokens entry and no tokens card, and neither package was imported
(scenarios 2 and 3, SC-005, FR-003).

### T008 — The decision record, the glossary and the first documentation

**Files**: `docs/adr/0005-the-package-provides-the-api-tokens-pages.md`,
`docs/adr/0002-account-management-lives-in-the-account-center.md`, `docs/adr/README.md`,
`README.md`, `CONTEXT.md`, `CHANGELOG.md`

FR-013 to FR-015. ADR 0005: the package provides the tokens pages itself because knox ships none,
what they are limited to (list, create, revoke over knox's records, no model), that the "Account"
group is now built without allauth too, and what would make it worth revisiting. ADR 0002 gains
one line pointing at ADR 0005 where it says the menu adds nothing without allauth. README: an "API
tokens" section on turning the feature on (the extra, knox in the installed apps and its
migrations, including the tokens URLs, knox's authentication class in the project's own settings,
and that none of it is checked), and API tokens in the Account Center list. `CONTEXT.md`: the API
token entry says a person chooses when each expires and sees its first characters and the days it
was created and expires, with no last-used time, and that it exists when the host project has
installed django-rest-knox and routed the pages. CHANGELOG `Added` entry under `[Unreleased]`.

---

## US3 — A person sees the tokens they hold (P2)

Issue: #39. Delivers FR-010 and US3's part of FR-001, FR-006, FR-016 and SC-003.

### T009 — The list

**Files**: `mvp_accounts/tokens/views.py`, `tests/test_tokens/test_views.py`

Research R1. Tests against the rendered page: a person with three tokens sees three rows, each
carrying its `token_key` and the days it was created and expires (scenario 1). Another person's
tokens are absent (scenario 2). No tokens renders without a table and still links to the create
page (scenario 3). A token with no expiry has a row with no date in its expiry cell and no empty
or zero date (scenario 4). An expired token is not listed (scenario 5). The page costs the same
number of queries with one token and with several.

### T010 — Seeded tokens in the demo

**Files**: `demo/management/commands/seed_demo.py`, `tests/test_demo.py`

FR-016. `seed_demo` gives `staff.user@example.com` three working tokens, one with no expiry, and
one that has expired, and gives `super.user@example.com` as many as the demo's limit. Each run
replaces them. Test: seeding twice leaves staff with three working tokens and one expired, and
super at the limit.

---

## US2 — A person creates an API token (P1)

Issue: #38. Delivers FR-007 to FR-009, FR-018 and US2's part of FR-001, FR-006, FR-015, FR-016,
SC-001 and SC-002.

### T011 — The lifetime form

**Files**: `mvp_accounts/tokens/forms.py`, `tests/test_tokens/test_forms.py`

D11. `CreateTokenForm` with one required choice, `lifetime`: 7 days, 30 days, 90 days, 1 year and
never, 30 days initial. `get_expiry()` returns a `timedelta`, or `None` for never. Tests: each
choice's expiry, the initial choice, and a value outside the list refused on the `lifetime` field.

### T012 — The create page

**Files**: `mvp_accounts/tokens/views.py`, `tests/test_tokens/test_views.py`

Plan *Views*. `CreateTokenView` renders the approved create template. Tests: loading the page
creates nothing (scenario 7). Submitting a lifetime creates one knox token for the signed-in
person, expiring that far from now, and redirects to the tokens page (scenarios 1 and 5).
"Never" stores no expiry (scenario 6). An invalid choice creates nothing and shows the form again.
Someone not signed in is sent to sign in.

### T013 — The token shown once

**Files**: `mvp_accounts/tokens/views.py`,
`tests/test_tokens/test_views.py`, `tests/test_components/__init__.py`,
`tests/test_components/test_token_created.py`, `pyproject.toml` (`non-mirror-paths`)

Research R3, plan *The one-time token*. Tests: following the redirect after creating, the page
holds the complete value, in the field with id `new-api-token` (scenario 1, FR-008). Loading the
tokens page again holds it nowhere (scenario 2, SC-002). After creating, no session key and no
database row holds the value. On the redirect response, the cookie carries the tokens page's
`path`, `httponly`, `samesite` and a `max-age`. On the response that reads it,
`response.cookies["mvp_accounts_new_token"]` carries `max-age` 0 and the same `path`. A tampered
or expired cookie shows nothing. Another person loading the tokens page with the first person's
cookie is shown no value. The page that shows the value is not cacheable. The view's `new_token`
carries the `token_key` of the record just created. The component renders the value it is given into that field and the header prefix it is given into
its example. Submitting the create form twice makes two tokens and reloading the tokens page makes
none.

### T014 — The limit

**Files**: `mvp_accounts/tokens/views.py`, `tests/test_tokens/test_views.py`

Research R1, R5. Tests under `override_settings(REST_KNOX=...)`: at the limit, loading or
submitting the create page creates nothing, adds an error-level message and redirects to the
tokens page (scenario 4, FR-009). The tokens page then has no link to the create page. An expired
token does not count and a token with no expiry does. With no limit set, creating is never
refused.

### T015 — A real request

**Files**: `demo/api.py`, `demo/urls.py`, `tests/test_demo.py`

FR-016. `demo/api.py` holds one view, `WhoAmIView`, that answers an authenticated request with
the person's email, routed at `api/whoami/`. It is a module of its own so the routes used without
knox can leave it out (research R6). Tests: a token created through the create page, sent in the
`Authorization` header, is answered as that person (scenario 3, SC-001). A request with no token
is refused.

### T016 — Documentation for creating

**Files**: `README.md`, `CHANGELOG.md`

FR-015. README: a token is shown once and what to do if it is lost. The lifetimes a person chooses
from. knox's `TOKEN_TTL` reaches only tokens knox's own views create, and `TOKEN_LIMIT_PER_USER`
is the limit the pages honour. knox sets no limit by default, so a project should set one. Tokens
carry no name or last-used time.

---

## US4 — A person revokes a token (P2)

Issue: #40. Delivers FR-011 and US4's part of FR-001, FR-006, FR-015 and SC-004.

### T017 — The confirmation page

**Files**: `mvp_accounts/tokens/views.py`, `tests/test_tokens/test_views.py`

Research R4, R5. `RevokeTokenView` takes one record, the newest of the person's working tokens
with that `token_key`. Tests: the tokens page links each row to its own confirmation page. Loading the
confirmation page shows that token and deletes nothing (scenario 6). Backing out leaves the token
working (scenario 4). A `token_key` that is someone else's, expired or unknown adds a message and
redirects to the tokens page, on GET and on POST, and all three get the same response
(scenario 5).

### T018 — Revoking

**Files**: `mvp_accounts/tokens/views.py`, `tests/test_tokens/test_views.py`,
`tests/test_demo.py`

Tests: submitting the confirmation deletes that token and no other, adds a success-level message
and redirects to the tokens page, which lists the rest (scenario 1). Through the demo's endpoint,
the revoked token is refused and another of the person's tokens is still answered (scenarios 2
and 3, SC-004). Another person submitting to the same address deletes nothing.

### T019 — Documentation for revoking

**Files**: `README.md`, `CHANGELOG.md`

FR-015. README: revoking asks first and takes effect at once. Changing a password does not revoke
tokens, and knox's own sign-out-everywhere endpoint deletes them all.

---

## US5 — A developer limits who may hold API tokens (P2)

Issue: #41. Delivers FR-019 and US5's part of FR-001, FR-006, FR-015, FR-016, FR-017 and SC-007.

### T020 — The access check

**Files**: `mvp_accounts/tokens/access.py`, `tests/test_tokens/test_access.py`

Research R7. `may_use_tokens(user)`. Tests: with no setting, a signed-in person may and an
anonymous visitor may not. With `MVP_ACCOUNTS_API_TOKEN_ACCESS` naming a function, its answer
decides, and it is not asked about an anonymous visitor. A path that does not import raises
`ImportError`.

### T021 — The pages refuse

**Files**: `mvp_accounts/tokens/views.py`, `tests/test_tokens/test_views.py`

Plan *Views*. `TokenPageMixin.test_func` now returns `may_use_tokens(self.request.user)`. Tests
with the setting letting in staff only: a person who is not staff gets 403 from the tokens page,
the create page and a confirmation page, loaded and submitted, and no token is created or deleted
(scenario 4). A refused person who is at the limit gets the 403 and not the limit redirect. A staff person is served as before
(scenario 2). With no setting everyone signed in is served (scenario 1). Someone not signed in is
still sent to sign in (scenario 5).

### T022 — The entry and the card follow it

**Files**: `mvp_accounts/menus.py`, `mvp_accounts/templatetags/__init__.py`,
`mvp_accounts/templatetags/mvp_accounts.py`,
`mvp_accounts/templates/mvp/account/overview.html`, `tests/test_menus.py`,
`tests/test_account_center.py`, `tests/test_templatetags/__init__.py`,
`tests/test_templatetags/test_mvp_accounts.py`, `tests/test_without_knox.py`

The entry gets a `check` that calls `may_use_tokens`. The card is drawn only when the
`may_use_api_tokens` tag says so. Tests: with the setting letting in staff only, the Account
Center of a person who is not staff has no entry and no card (scenario 3, SC-007), and a staff
person's has both. The tag answers for the request's user and is false without a request. The
runs without knox still pass, which shows the tag and the check import nothing from it.

### T023 — The demo lets in staff only, and the documentation

**Files**: `demo/access.py`, `demo/settings.py`, `tests/settings.py`,
`demo/management/commands/seed_demo.py`, `tests/test_demo.py`, `README.md`, `CHANGELOG.md`

FR-015, FR-016. `demo.access.staff_only` and the setting in the demo. The suite's settings remove
`MVP_ACCOUNTS_API_TOKEN_ACCESS`, so the suite runs the package's default and no earlier test is
edited. The tests here set `demo.access.staff_only` with `override_settings`. The seed command's
docstring and closing output say who holds what and that `regular.user@example.com` may not hold
tokens. Tests: after `seed_demo`, the regular account is refused at the tokens page and the staff
account sees its three tokens. README: the setting, its default, an example function, and that it
does not revoke tokens a person already holds and is not consulted when a token is used.

### T024 — The translation catalogue

**Files**: `mvp_accounts/locale/en/LC_MESSAGES/django.po`

FR-017, research R10. `makemessages -l en` from inside `mvp_accounts/`. Check that every string
this feature added is in the catalogue.
