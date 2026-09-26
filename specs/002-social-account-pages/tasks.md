# Tasks — 002 Sign in with social accounts

**Branch**: `002-social-account-pages` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it.

## Order

**US1 → US2, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — Sign in or sign up with an external account (P1)

Issue: #16. Delivers FR-001, FR-002, FR-004 to FR-006, FR-009 to FR-011, US1's part of FR-008 and
FR-012, and SC-001 to SC-003 and US1's part of SC-005.

### T001 — The social account app and the test provider in the demo

**Files**: `demo/settings.py`, `tests/settings.py`, `tests/settings_without_allauth.py` (only if a
new setting names allauth), `tests/test_demo.py`

Research R5, R6. `allauth.socialaccount` and `allauth.socialaccount.providers.dummy` after
`allauth.account` in `INSTALLED_APPS`. `EASY_ICONS["default"]["icons"]["dummy"]` mapped to a
Bootstrap icon class, with a comment saying the project, not the package, supplies provider icons.
The suite's settings add `allauth.socialaccount.providers.github` and a GitHub app configured in
`SOCIALACCOUNT_PROVIDERS` (placeholder client id and secret), so the suite lists two providers; the
comment says why. `tests/settings_without_allauth.py` must still strip every allauth app, including
the providers; check that its filter does. Tests: the test provider's login URL resolves in the demo.

### T002 — Provider buttons

**Files**: `mvp_accounts/templates/allauth/elements/provider.html`,
`mvp_accounts/templates/allauth/elements/provider_list.html`, `tests/adapters.py`,
`tests/test_social_entrance_pages.py`, `pyproject.toml` (`non-mirror-paths`)

Research R2. `provider` draws `<c-button>` with `href` from `attrs.href`, `icon` from
`attrs.provider_id`, the display name `attrs.name` as its visible text, and a `title` of the name.
`provider_list` wraps the buttons in a wrapping row, like FS-001's non-vertical `button_group`. A
comment in `provider.html` says the icon is named after allauth's provider id and that the host
project supplies it. Tests on the sign-in and sign-up pages: exactly two buttons (GitHub and the
test provider), each with its name as text, each linking to that provider's login URL, and each
carrying the icon markup the icon mapping produces for its provider id (SC-003). With a test social
adapter whose `list_providers` returns `[]` (`override_settings(SOCIALACCOUNT_ADAPTER=…)`): no
provider button, and none of the snippet's divider or "Or use a third-party" heading (acceptance
scenario 2, SC-002).

### T003 — The social entrance pages

**Files**: `tests/test_social_entrance_pages.py`

Research R1, R5. Driven through the test provider, each page asserts the plan's four page
assertions as an entrance page:

- the confirmation page (GET of the test provider's login URL), with allauth's "Continue" button;
- the test provider's own form;
- the extra sign-up step: post the test provider's form without an email, land on
  `socialaccount_signup`; then post that step with an invalid email and assert the field error is
  on the page (FR-008);
- the cancelled page (post the test provider's form with `action=cancel`);
- the failed page (`socialaccount_login_error`);
- a completed sign-in: post the test provider's form with an id and a verified email, and end
  signed in.

### T004 — The same-site redirect page

**Files**: `mvp_accounts/templates/socialaccount/login_redirect.html`,
`tests/test_social_entrance_pages.py`

Research R1. Extends `socialaccount/base_entrance.html`; `head_title` as allauth's ("Sign In" and
the provider); the `<meta http-equiv="refresh">` in `extra_head`; allauth's "Continue" link to
`redirect_to` in `content`, through the `p` element. Test: a GET to the GitHub callback URL under
`override_settings(SESSION_COOKIE_SAMESITE="Strict")` renders it as an entrance page and keeps the
refresh to the same URL with `_redir`.

### T005 — Documentation

**Files**: `README.md`, `CHANGELOG.md`

FR-010. A README section on signing in with other accounts: install `allauth.socialaccount` and the
providers the project wants, as allauth documents; one button per provider allauth lists, with the
provider's name; each button's icon is named after allauth's provider id (`github`, `google`), so
the project's django-easy-icons setup needs an icon under each configured id; a missing one raises
unless `EASY_ICONS_FAIL_SILENTLY` is set, in which case the button shows its name alone; the
package ships no provider icons and checks none. Mention that OpenID brands all use the `openid`
icon. CHANGELOG `Added` entry under `[Unreleased]`.

---

## US2 — Connect and disconnect external accounts (P2)

Issue: #17. Delivers FR-003, FR-007, US2's part of FR-008 and FR-012, SC-004 and US2's part of
SC-005.

### T006 — The Connected accounts entry

**Files**: `mvp_accounts/menus.py`, `tests/test_menus.py`

Research R4. One more child of the existing "Account" `MenuGroup`, after Phone number:
`MenuItem(name="connections", view_name="socialaccount_connections", extra_context={"label":
_("Connected accounts"), "icon": "link"})`. No `MenuCollapse`, no top-level entry, no guard of its
own. Update the module docstring's list of what is left out when not routed. Test: the rendered
Account Center menu has "Connected accounts" inside the "Account" group.

### T007 — The Connected accounts card

**Files**: `mvp_accounts/templates/mvp/account/overview.html`, `tests/test_account_center.py`

Research R4. A card after the phone card, resolved with `{% url "socialaccount_connections" as
connections_url %}` and drawn only when it resolves, icon `link`, a translatable sentence, and a
"Manage connected accounts" button. Test: the card is on the Account Center landing page for a
signed-in person.

### T008 — The connections page

**Files**: `mvp_accounts/templates/socialaccount/connections.html`, `tests/factories.py`,
`tests/test_connections_page.py`, `pyproject.toml` (`non-mirror-paths`)

Research R3, R5. `SocialAccountFactory` (test provider, sequential uid, a user from
`UserFactory`). The page extends `socialaccount/connections.html` and adds to `content` through
`{{ block.super }}`: when `form.non_field_errors`, an error alert through allauth's `alert`
element, before allauth's markup. Tests, each asserting the plan's four assertions as a management
page:

- one connected account: listed with allauth's "Remove" action, provider buttons shown with
  `process=connect` links;
- none connected: allauth's "no third-party accounts" sentence and the provider buttons;
- refusal: a person with an unusable password and one connected account posts the form, and
  allauth's "Your account has no password set up." is on the page (FR-008);
- connecting: signed in, follow the test provider's `process=connect` button through its
  confirmation and form, and the new account is listed on the connections page (SC-005);
- a successful disconnect for a person with a password redirects, and allauth's message appears on
  the page it lands on.

### T009 — Without the social account app

**Files**: `tests/settings_without_socialaccount.py`, `tests/test_without_socialaccount.py`,
`tests/test_without_allauth.py` (only to share the subprocess runner), `pyproject.toml`
(`non-mirror-paths`)

Research R5. Settings from the suite's with every `allauth.socialaccount` app and
`SOCIALACCOUNT_PROVIDERS` removed, allauth kept. A subprocess like FS-001's: the Account Center
and its landing page render with 200, "Connected accounts" is on neither, the sign-in page renders
with no provider button, and nothing raises (SC-004). Share the runner with
`test_without_allauth.py` rather than copying it.

### T010 — Demo states, catalogue and documentation

**Files**: `demo/management/commands/seed_demo.py`, `tests/test_demo.py`,
`mvp_accounts/locale/en/LC_MESSAGES/django.po`, `README.md`, `CHANGELOG.md`

Research R6. `seed_demo` gives the staff account a connected test-provider account and creates
`social.user@example.com` with an unusable password, a verified primary address and one connected
test-provider account, both idempotent; the command's docstring names the states. Test: running
`seed_demo` twice leaves one of each. `makemessages -l en` from inside `mvp_accounts/`. README's
Account Center section lists Connected accounts and says it appears only with the social account
app installed. CHANGELOG `Added` entry.
