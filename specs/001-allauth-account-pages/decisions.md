# Decisions — 001 Accounts, sign-in and recovery on the site's own pages

## D1 — allauth is a development dependency only

The package reskins allauth by putting templates where allauth's template lookup finds them. Those
templates are only ever loaded by allauth's own views, so a project without allauth never touches
them, and a project with allauth gets them without the package doing anything at runtime. Declaring
allauth as a runtime dependency would add nothing the host project does not already have when it
wants these pages, and would force it on projects that do not.

The constitution (Article XIII) asks for every upstream dependency to be bounded to the major versions
CI runs. With allauth in the development group only, that bound applies to what CI installs and
cannot reach a host project. The README therefore states the supported range, and the bound in the
development group keeps CI on it.

**ADR:** docs/adr/0001-reskin-allauth-through-its-templates.md

## D2 — No configuration checks

The package does not check allauth's middleware, authentication backends, settings or URL
configuration. Setting allauth up is the host project's job, and allauth documents it. The only
adoption step this package adds, listing it ahead of `allauth` in `INSTALLED_APPS`, is documented
rather than checked.

**ADR:** docs/adr/0001-reskin-allauth-through-its-templates.md

## D3 — Sign-up by passkey belongs to two-factor authentication

`account/signup_by_passkey.html` ships in allauth's account app, but the page only exists when
allauth's multi-factor app is installed and passkey sign-up is enabled. It is reskinned and tested
with the rest of the multi-factor pages in #7.

**ADR:** none — a scope boundary for this feature, recorded in the spec

## D4 — Glossary correction

`CONTEXT.md` says closing an account is something the authentication package provides. allauth has
no account deletion. The implementation corrects the entry (FR-013), and account deletion stays out
of this feature. It is either a request to allauth or a data-rights concern for django-mvp-compliance.

**ADR:** none — a wording fix to CONTEXT.md, nothing downstream inherits it

## D5 — The overview is the Account Center, and the menu entries are the shell's

The spec's "Account" and "Sign out" are the entries django-mvp's user menu already draws: its
Account Center, and sign-out posting to `account_logout`, which is allauth's once allauth is
installed. The account overview is the Account Center's landing page. This package adds a menu
entry and a card per management page to that area rather than a second overview beside it. The
labels are django-mvp's ("Account Center", "Log out"); renaming them is a change to the shell.
Without allauth this package contributes nothing to either, and what django-mvp draws on its own
is the shell's. Research R5.

**ADR:** docs/adr/0002-account-management-lives-in-the-account-center.md

## D6 — allauth's management pages lose the Account Center's container until django-mvp#358 ships

allauth's pages fill `{% block content %}`, which replaces the Account Center layout's own
`content` block and the container inside it. The page keeps the shell, its sidebar and its
messages, so FR-003 holds. The container's padding is missing until django-mvp#358 is fixed
upstream. A test asserting the container is written and skipped naming that issue, and the
layout needs no change when the fix ships. Research R3.

**ADR:** none — a temporary upstream limitation, tracked by the skipped test and django-mvp#358

## D7 — The package goes ahead of both allauth and django-mvp in INSTALLED_APPS

Ahead of `allauth` so its layouts and elements win, which the spec names. Ahead of `mvp` as well,
because the overview cards reach the Account Center by shipping `mvp/account/overview.html`,
and Django only reaches it before django-mvp's own copy when this app is listed first. It is
still one adoption step: where the package goes in the list. The README says both.

**ADR:** docs/adr/0001-reskin-allauth-through-its-templates.md

## D8 — One demo configuration, the other halves reached by the tests

Reset by code or by link, and email verification by code or by link, are chosen when allauth's
URLconf is imported, so one demo cannot show both halves of either. The demo runs the defaults
(link) with code sign-in, phone numbers and re-authentication turned on. The tests rebuild the
URLconf to reach the code halves. Research R6, R7.

**ADR:** none — local to the demo and the test suite

## D9 — Four pages change base, three by copying allauth's markup

Sign-out and "verified email required" sit on allauth's management base, and re-authentication
and phone verification on its entrance base, the opposite of the spec's split. The entrance base
is overridden to follow the visitor, management when signed in, which settles re-authentication
and phone verification in one line and matches `CONTEXT.md`'s definition of an entrance page.
Sign-out and "verified email required" are copies of allauth 65.19.4's pages with the parent
switched, because they are always seen signed in and the spec still makes them entrance pages.
Those two copies are what has to be compared against allauth's on each release. Research R1.

**ADR:** docs/adr/0001-reskin-allauth-through-its-templates.md

## D10 — What "offers" means when sign-up is closed

allauth's sign-in page links to sign-up whether sign-up is open or not, and following the link
shows allauth's "sign-up closed" page. FR-005 forbids this package adding or removing what allauth
renders, so the link stays. SC-004's sign-up case is read as: the package offers nothing extra,
and the sign-up page is the closed page. Removing allauth's link would mean overriding its
sign-in page, which is a request to allauth.

**ADR:** none — a reading of one success criterion, local to this feature

## D11 — The spec's "no account menu entry" without allauth means this package's entries

A project without allauth that includes `mvp.urls` still has django-mvp's Account Center, its
user-menu entry and a development-only sign-out. Those are the shell's, drawn whether or not this
package is installed. US3 scenario 5 and SC-003 are read as this package contributing no entry,
no card and no route, which the no-allauth test asserts.

**ADR:** docs/adr/0002-account-management-lives-in-the-account-center.md

## D12 — FR-012 is met by the demo and the tests together

The pages behind reset by code and email verification by code cannot exist in the same
configuration as their by-link counterparts. The demo reaches the by-link halves and the tests
reach the rest.

**ADR:** none — a reading of one requirement, local to this feature

## D13 — Watch items from the design review

- An element override never passes an attribute value through `|safe`. allauth hands elements
  values such as `href=alt.url`, and autoescaping is the control.
- `tests/test_apps.py` mirrors `mvp_accounts/apps.py`, and `tests/test_app.py` covers the
  installed app's on-disk layout. Each module's docstring says which it is.

**ADR:** none — review watch items, not decisions

## D14 — The field element passes only the attributes the account pages use

`allauth/elements/field.html` draws through `<c-form.field>` and forwards `type`, `id`, `name`,
`value`, `errors`, `checked` and `disabled`, which are the attributes allauth's account pages give
it. `required`, `readonly`, `placeholder`, `autocomplete` and `rows` are not forwarded. Cotton writes
every attribute it is given, so a false value would still switch the control on (`checked="False"`
ticks a box), and each attribute that has to be conditional doubles the branches in the template.
`checked` and `disabled` already need a branch each. **Revisit if** an allauth page in the supported
range passes one of the others to `field`.

**ADR:** none — sealed inside one template

## D15 — `rebuild_urls` reloads allauth's views as well as its URLconf

The email page's template is chosen by a class attribute of its view, read when the module is
imported (`ACCOUNT_CHANGE_EMAIL` picks between two templates), so reloading only the URLconf left the
old template in place. The fixture reloads `allauth.account.views` first. **Revisit if** a supported
allauth release moves that choice to request time.

**ADR:** none — test infrastructure

## D16 — The "verified email required" test passes without its override, for now

allauth's page extends `account/base_manage.html`, which extends `allauth/layouts/manage.html`.
That layout is not in the package yet, so allauth's own is found, and it extends
`allauth/layouts/base.html`, which the package sends to the entrance layout. The page therefore
rendered as an entrance page before the copy existed, and its test was never red. The copy is added
anyway: once the management layout exists, the page would otherwise take it. **Revisit if** the test
is not red when the copy's `{% extends %}` is pointed back at `account/base_manage.html` after the
management layout lands.

**ADR:** none — a note on one test's history; the override itself is ADR 0001

## D17 — The user menu is asserted on the demo overview page, not the Account Center

**Decision:** T013 reads the shell's user menu off the demo's overview page.
**Why:** On the Account Center itself django-mvp draws its own navigation in place of the menu's "Account Center" row, and the sidebar's Overview entry links to the same URL, so a link assertion there passes with the user menu removed.
**Revisit if:** django-mvp draws the row on the Account Center too.

**ADR:** none — test detail

## D18 — flex_menu is a declared transitive dependency

**Decision:** `menus.py` imports `flex_menu.MenuItem`; deptry's DEP003 ignore in `pyproject.toml` names it instead of adding a direct requirement.
**Why:** django-mvp requires the menu library and documents `from flex_menu import MenuItem` as how a project extends its menus, so its requirement is the pin that matters.
**Revisit if:** django-mvp stops requiring it.

**ADR:** none — follows the convention every package built on django-mvp uses

## D19 — The allauth guard lives in menus.py, and ready() adds nothing

**Decision:** `mvp_accounts/menus.py` adds its entries only when `allauth.account` is installed, and `MvpAccountsConfig` has no `ready()`. This departs from the brief, which had `ready()` import the module.
**Why:** django-flex-menus imports the `menus` module of every installed app when it starts, so a guard in `ready()` never stopped the import. Without allauth the entries were on the menu and the pages raised on their unresolvable URLs; the subprocess test showed it.
**Revisit if:** the menus module is renamed so it is no longer autodiscovered, when a `ready()` import would be the guard again.

**ADR:** docs/adr/0002-account-management-lives-in-the-account-center.md

## D20 — The warning snippet is overridden because allauth draws it as a paragraph

**Decision:** `account/snippets/warn_no_email.html` is this package's copy of allauth's three-line snippet, drawing the warning through `{% element alert tags="warning" %}`.
**Why:** allauth 65.19.4 renders it with `{% element p %}`, which the elements draw as body copy. The brief asks for an alert, and the alert element already maps the `warning` tag to django-mvp's warning variant, so the copy is the only change.
**Revisit if:** allauth's own snippet moves to the alert element.

**ADR:** none — sealed inside one template

## D21 — The phone verification test asserts the page, not the stored number

**Decision:** the signed-in phone verification test asserts the redirect back to the phone page and allauth's "You have verified phone number" message, not a `PhoneNumber` row.
**Why:** the page is this package's concern and the stored number is the demo adapter's. The adapter has its own test that a verified change is stored (`tests/test_demo.py::TestDemoAccountAdapter`).

**ADR:** none — test detail

## D22 — A signed-in person opening password reset gets the management layout

FR-002 lists password reset among the entrance pages. allauth builds it on its entrance base, which
this package sends to the management layout for a signed-in person (D9). A signed-in person
resetting their password is still signed in, and `CONTEXT.md` defines an entrance page as one seen
before signing in, so the management layout is kept and pinned by a test. Signed out, which is how
password reset is used, it is an entrance page as FR-002 says.

**ADR:** docs/adr/0001-reskin-allauth-through-its-templates.md

## D23 — The review fixes were made directly, without a dispatch

Three one-line changes and their tests: the "Request new code" button's default type, a test that
verification by link offers no code, and a test pinning D22. Dispatching an Implementer for each
would have cost more than the change.

**ADR:** none — a note on how this run worked
