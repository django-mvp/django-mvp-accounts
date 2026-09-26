# Decisions — 002 Sign in with social accounts

## D1 — Provider icons are named by provider id and supplied by the host project

Each provider button renders `<c-icon>` with allauth's provider id as the name. The id is stable and
lowercase, which is how icon names are keyed in django-easy-icons, while the display name can carry
capitals and spaces. The package ships no provider icons and does not check for them: which icon set
a project uses is its own choice, and supplying icons for every provider allauth supports would
make this package a brand-asset catalogue.

## D2 — A missing provider icon behaves as django-easy-icons decides

django-easy-icons raises for an unknown name unless `EASY_ICONS_FAIL_SILENTLY` is set. The package
does not catch this or fall back, in line with FS-001's rule that configuration is the host
project's and is not checked here. The README states the requirement.

## D3 — The connected-accounts entry follows whether allauth routes the page

The Account Center entry and card appear when allauth's connections URL resolves, the same test
FS-001 uses for every management page, so they appear with the social account app installed even
before any provider is configured.

## D4 — The demo uses allauth's test provider

`allauth.socialaccount.providers.dummy` completes a sign-in without leaving the machine, so every
page in the feature, including the extra sign-up step and the error page, can be reached in the demo
and in tests without real credentials.

## D5 — "Connected accounts" carries no guard of its own

It is one more child of the "Account" group, which is added only when `allauth` is installed.
allauth routes the connections page only when `allauth.socialaccount` is installed, and django-mvp
drops an entry whose URL does not resolve, so the entry follows the app with no check here. An
`is_installed("allauth.socialaccount")` guard would state that fact twice and add a branch only a
separate process could measure (research R4).

## D6 — The refusal to disconnect is drawn by the connections page

allauth reports it as a non-field error, and nothing draws non-field errors on a page that does not
render its form through `fields` (research R3). Drawing them in the `form` element would print them
twice on every page that does. The package's `socialaccount/connections.html` extends allauth's
template of the same name and adds the alert before allauth's markup, the same chaining FS-001's
overview uses.

## D7 — The same-site redirect page is reskinned

It is a page the social account app renders, so FR-001 reaches it, though a project only sees it
with `SESSION_COOKIE_SAMESITE = "Strict"`. It is the one social account page that extends nothing,
so it gets a page override keeping allauth's refresh and link (research R1).

## D8 — The suite lists two providers, the demo one

FR-011 asks the demo for the test provider only. Acceptance scenario 1 needs two, so the suite's
settings add GitHub with an app configured in settings, which needs no database row, and whose
icon django-mvp's pack already names (research R5).

## D9 — The confirmation page is an entrance page for a signed-in person too

allauth's social account pages extend its entrance layout directly, not through
`account/base_entrance.html`, so FS-001's rule that a signed-in person gets the management layout
does not reach them. FR-002 asks for exactly this, so nothing is changed (research R1).
