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
