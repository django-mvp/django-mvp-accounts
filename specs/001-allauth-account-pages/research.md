# Research — 001 Accounts, sign-in and recovery on the site's own pages

Each entry records a decision the plan rests on, why it was taken, and what else was considered.
Versions read: django-allauth 65.19.4, django-mvp 0.25.0.

## R1 — How allauth's pages reach the shell

**Decision**: override allauth's three layout templates, `allauth/layouts/base.html`,
`allauth/layouts/entrance.html` and `allauth/layouts/manage.html`, from this package's
`templates/` directory.

**Rationale**: every page in allauth's account app extends `account/base_entrance.html` or
`account/base_manage.html`, and those two extend `allauth/layouts/entrance.html` and
`allauth/layouts/manage.html`. Both of those extend `allauth/layouts/base.html`. Overriding the
two layouts moves every account page, including one a later 65.x release adds, without touching
any page template. `base.html` is overridden as well so that anything extending it directly (none
of the account app's pages do in 65.19.4) lands on the entrance layout rather than allauth's bare
HTML document.

allauth's pages fill four blocks: `head_title`, `extra_head`, `content` and `extra_body`. The
layouts map them onto the shell's `title`, `head`, `content` and `extra_js`.

**Alternatives**: overriding each page template (about thirty files that would each need
revisiting on every allauth release, and the thing Article XIII rules out), or a custom view
layer (reimplements allauth).

## R2 — The entrance layout

**Decision**: `allauth/layouts/entrance.html` extends `mvp/entrance.html`, overrides its
documented `entrance` block to restate `<c-entrance>` at `size="md"` with `<c-messages>` above
it, and nests `{% block content %}` inside.

**Rationale**: `mvp/entrance.html` is django-mvp's page for anonymous-facing views. It renders
the theme and the stylesheet and replaces the whole `app` block, so no sidebar, header or dock
is drawn (FR-002). Overriding `entrance` to choose a card width is the use its own comment
documents, and `md` is the width django-mvp's own sign-in page uses. `mvp/entrance.html` does
not render messages, and allauth adds them on entrance pages ("Confirmation email sent", the
sign-out message when a project redirects to an entrance page), so the layout draws
`<c-messages>` itself from django-mvp's component.

## R3 — The management layout and django-mvp#358

**Decision**: `allauth/layouts/manage.html` extends `mvp/account/base.html`, the Account
Center's layout, and maps allauth's blocks. The one thing this loses is recorded as a skipped
test naming django-mvp#358, and not worked around.

**Rationale**: `mvp/account/base.html` in 0.25.0 extends the project's own `base.html` and wraps
`{% block content %}` in a container, offering pages `account.content` inside it. allauth's
pages fill `content`, which replaces the layout's own `content` block, container included. What
survives is everything that matters for FR-003: the page is inside the shell with its sidebar,
header and messages. The Account Center's navigation is drawn in the shell's sidebar since
0.25.0, not in the page body, so the page keeps it whenever an `AccountCenterMenu` entry marks
the page current (R5). What is lost is the container's padding. django-mvp#358 proposes the fix
upstream (the layout claims `app.main` and leaves `content` free), and once it ships this layout
needs no change. A test asserting the container is written now and skipped with that issue in
its reason.

**Alternatives**: a layout of this package's own restating the shell's arrangement (the
workaround the upstream issue exists to retire), or extending `page_view.html` (takes
`page.content`, the same collision).

## R4 — allauth's elements

**Decision**: override the shared elements under `allauth/elements/` that the account app's
pages use, building each from django-mvp's components: `alert`, `badge`, `button`,
`button_group`, `details`, `field`, `fields`, `form`, `h1`, `h2`, `hr`, `img`, `p`, `panel`,
and the table set (`table`, `thead`, `tbody`, `tr`, `th`, `td`). `provider` and
`provider_list` belong to social accounts and are left to that feature.

**Rationale**: FR-004. A whole form goes through `fields`, which renders with django-mvp's
`<c-form.render>`, so allauth's forms look like every other form on the site and field errors
and non-field errors appear where the site's other forms show them. `field` is used directly for
single hand-built inputs (the email radio list, code inputs) and is built on `<c-form.field>`
where that component can carry what allauth passes, keeping the label, help text and errors
associated with the input (FR-015). allauth's `unlabeled` hint is ignored: every field keeps a
visible label.

## R5 — Where "Account" and "Sign out" come from

**Decision**: the account overview is django-mvp's Account Center landing page, and the user
menu entries are django-mvp's own. This package adds to the Account Center rather than beside
it: an entry per management page in `AccountCenterMenu`, and a card per management page on the
landing page through `mvp/account/overview.html`'s `account.cards` block.

**Rationale**: django-mvp 0.25.0 ships the user menu with an entry for the Account Center
whenever `account-center` resolves and a sign-out entry whenever `account_logout` resolves, and
withdraws its own development-only sign-in and sign-out once `allauth.account` is installed
(its ADR 0024). The spec's assumptions put the user menu and the message display with the shell.
A second "Account" entry beside the shell's would give the menu two ways to the same place.
The card mechanism is the extension point django-mvp documents: an app ships its own
`mvp/account/overview.html`, extends the same name and adds through `{{ block.super }}`, so
later features chain on without touching this one (FR-007).

The entries' labels are django-mvp's ("Account Center", "Log out"). The spec calls them
"Account" and "Sign out", and changing either label is a change to the shell, not to this
package.

**Consequence for FR-006/FR-008**: without allauth this package contributes no menu entry and no
card, and its templates are never loaded. The Account Center and the stand-in sign-out that
django-mvp draws in a project without allauth are the shell's.

## R6 — Menu entries and cards appear only for what the project has on

**Decision**: register the `AccountCenterMenu` entries from `MvpAccountsConfig.ready()` only
when `allauth.account` is installed. Each entry names its allauth URL, and each card resolves
its URL with `{% url … as %}` and draws nothing when it does not resolve.

**Rationale**: allauth decides which account URLs exist when its URLconf is imported: the phone
pages exist only when `"phone"` is in `ACCOUNT_SIGNUP_FIELDS`, the reset-by-code pages only
with `ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED`, and so on. flex_menu drops an entry whose URL
does not resolve, and a card can ask the same question in the template, so the one source of
truth for "is this on" is allauth's own URLconf (FR-005). No setting is read and no system check
added (FR-009).

Tests that switch one of those settings have to rebuild the URLconf, since allauth read it at
import: `override_settings` plus reloading `allauth.account.urls` and the test urlconf, then
`clear_url_caches()`, with the reverse applied on teardown. One fixture in `tests/conftest.py`
does it.

## R7 — The demo project

**Decision**: the demo installs `allauth` and `allauth.account` after `mvp_accounts`, adds
allauth's middleware and authentication backend, mounts `allauth.urls` at `accounts/` and
`mvp.urls` at the root, sends email to the console, and turns on: sign-in by emailed code,
mandatory email verification by link, phone numbers, and re-authentication before sensitive
changes. Password reset is by link. A demo account adapter stores phone numbers in a demo-only
model and prints SMS codes to the console. `seed_demo` also creates each account's primary,
verified email address.

**Rationale**: FR-012. Some behaviours exclude each other at import time (reset by code or by
link, email verification by code or by link), so one demo configuration cannot reach both
halves of each. The demo takes the defaults a typical project runs, and the tests reach the
other halves through R6's fixture. allauth's phone support needs an adapter that stores numbers,
because allauth has no phone model of its own. Without verified addresses the seeded accounts
could not sign in under mandatory verification.

## R8 — Proving the absent-allauth case

**Decision**: a test runs a short script in a subprocess under `tests/settings_without_allauth.py`,
which inherits the test settings and removes allauth's apps, middleware, backend and URLs. The
script imports the package, builds the menus and renders the demo's pages and the Account Center
through the test client.

**Rationale**: FR-008 and SC-003. `INSTALLED_APPS` cannot be changed reliably inside a running
test process once app registries and URLconfs are loaded, and a subprocess tests exactly what a
project without allauth gets.

## R9 — The supported allauth range

**Decision**: `django-allauth>=65.19.4,<66` in the development dependency group, and the same
range stated in the README.

**Rationale**: the spec's clarification and Article XIII. The bound cannot reach a host project,
so the README carries it for them.

## R10 — django-mvp floor

**Decision**: raise the runtime floor from `django-mvp>=0.24.0` to `>=0.25.0`.

**Rationale**: 0.25.0 moved the Account Center's navigation into the sidebar, which is what lets
allauth's pages keep it despite django-mvp#358 (R3), and withdraws its own sign-in and sign-out
URL names once allauth is installed, so which view answers `account_logout` no longer depends on
URLconf order.
