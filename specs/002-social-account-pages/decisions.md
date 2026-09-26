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
