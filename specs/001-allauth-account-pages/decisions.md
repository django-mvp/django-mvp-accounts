# Decisions — 001 Accounts, sign-in and recovery on the site's own pages

## allauth is a development dependency only

The package reskins allauth by putting templates where allauth's template lookup finds them. Those
templates are only ever loaded by allauth's own views, so a project without allauth never touches
them, and a project with allauth gets them without the package doing anything at runtime. Declaring
allauth as a runtime dependency would add nothing the host project does not already have when it
wants these pages, and would force it on projects that do not.

The constitution (Article XIII) asks for every upstream dependency to be bounded to the major versions
CI runs. With allauth in the development group only, that bound applies to what CI installs and
cannot reach a host project. The README therefore states the supported range, and the bound in the
development group keeps CI on it.

## No configuration checks

The package does not check allauth's middleware, authentication backends, settings or URL
configuration. Setting allauth up is the host project's job, and allauth documents it. The only
adoption step this package adds, listing it ahead of `allauth` in `INSTALLED_APPS`, is documented
rather than checked.

## Sign-up by passkey belongs to two-factor authentication

`account/signup_by_passkey.html` ships in allauth's account app, but the page only exists when
allauth's multi-factor app is installed and passkey sign-up is enabled. It is reskinned and tested
with the rest of the multi-factor pages in #7.

## Glossary correction

`CONTEXT.md` says closing an account is something the authentication package provides. allauth has
no account deletion. The implementation corrects the entry (FR-013), and account deletion stays out
of this feature. It is either a request to allauth or a data-rights concern for django-mvp-compliance.

## The overview is the Account Center, and the menu entries are the shell's

The spec's "Account" and "Sign out" are the entries django-mvp's user menu already draws: its
Account Center, and sign-out posting to `account_logout`, which is allauth's once allauth is
installed. The account overview is the Account Center's landing page. This package adds a menu
entry and a card per management page to that area rather than a second overview beside it. The
labels are django-mvp's ("Account Center", "Log out"); renaming them is a change to the shell.
Without allauth this package contributes nothing to either, and what django-mvp draws on its own
is the shell's. Research R5.

## allauth's management pages lose the Account Center's container until django-mvp#358 ships

allauth's pages fill `{% block content %}`, which replaces the Account Center layout's own
`content` block and the container inside it. The page keeps the shell, its sidebar and its
messages, so FR-003 holds. The container's padding is missing until django-mvp#358 is fixed
upstream. A test asserting the container is written and skipped naming that issue, and the
layout needs no change when the fix ships. Research R3.

## The package goes ahead of both allauth and django-mvp in INSTALLED_APPS

Ahead of `allauth` so its layouts and elements win, which the spec names. Ahead of `mvp` as well,
because the overview cards reach the Account Center by shipping `mvp/account/overview.html`,
and Django only reaches it before django-mvp's own copy when this app is listed first. It is
still one adoption step: where the package goes in the list. The README says both.

## One demo configuration, the other halves reached by the tests

Reset by code or by link, and email verification by code or by link, are chosen when allauth's
URLconf is imported, so one demo cannot show both halves of either. The demo runs the defaults
(link) with code sign-in, phone numbers and re-authentication turned on. The tests rebuild the
URLconf to reach the code halves. Research R6, R7.

## Four pages change base, three by copying allauth's markup

Sign-out and "verified email required" sit on allauth's management base, and re-authentication
and phone verification on its entrance base, the opposite of the spec's split. The entrance base
is overridden to follow the visitor, management when signed in, which settles re-authentication
and phone verification in one line and matches `CONTEXT.md`'s definition of an entrance page.
Sign-out and "verified email required" are copies of allauth 65.19.4's pages with the parent
switched, because they are always seen signed in and the spec still makes them entrance pages.
Those two copies are what has to be compared against allauth's on each release. Research R1.

## What "offers" means when sign-up is closed

allauth's sign-in page links to sign-up whether sign-up is open or not, and following the link
shows allauth's "sign-up closed" page. FR-005 forbids this package adding or removing what allauth
renders, so the link stays. SC-004's sign-up case is read as: the package offers nothing extra,
and the sign-up page is the closed page. Removing allauth's link would mean overriding its
sign-in page, which is a request to allauth.

## The spec's "no account menu entry" without allauth means this package's entries

A project without allauth that includes `mvp.urls` still has django-mvp's Account Center, its
user-menu entry and a development-only sign-out. Those are the shell's, drawn whether or not this
package is installed. US3 scenario 5 and SC-003 are read as this package contributing no entry,
no card and no route, which the no-allauth test asserts.

## FR-012 is met by the demo and the tests together

The pages behind reset by code and email verification by code cannot exist in the same
configuration as their by-link counterparts. The demo reaches the by-link halves and the tests
reach the rest.

## Watch items from the design review

- An element override never passes an attribute value through `|safe`. allauth hands elements
  values such as `href=alt.url`, and autoescaping is the control.
- `tests/test_apps.py` mirrors `mvp_accounts/apps.py`, and `tests/test_app.py` covers the
  installed app's on-disk layout. Each module's docstring says which it is.

## The field element passes only the attributes the account pages use

`allauth/elements/field.html` draws through `<c-form.field>` and forwards `type`, `id`, `name`,
`value`, `errors`, `checked` and `disabled`, which are the attributes allauth's account pages give
it. `required`, `readonly`, `placeholder`, `autocomplete` and `rows` are not forwarded. Cotton writes
every attribute it is given, so a false value would still switch the control on (`checked="False"`
ticks a box), and each attribute that has to be conditional doubles the branches in the template.
`checked` and `disabled` already need a branch each. **Revisit if** an allauth page in the supported
range passes one of the others to `field`.

## `rebuild_urls` reloads allauth's views as well as its URLconf

The email page's template is chosen by a class attribute of its view, read when the module is
imported (`ACCOUNT_CHANGE_EMAIL` picks between two templates), so reloading only the URLconf left the
old template in place. The fixture reloads `allauth.account.views` first. **Revisit if** a supported
allauth release moves that choice to request time.
