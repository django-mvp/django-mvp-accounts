# ADR 0003 — Provider icons come from the host project

**Status:** accepted

## Decision

Each "sign in with" button renders django-mvp's `<c-icon>` under allauth's provider id (`github`,
`google`, `openid`), with the provider's display name as the button's text. This package ships no
provider icons, maps no icon names and never checks that one exists. A project that configures a
provider adds an icon under that id to its own django-easy-icons setup. What a missing icon does is
django-easy-icons' decision: `EASY_ICONS_FAIL_SILENTLY` defaults to `DEBUG`, so the button shows
its name alone in development and the page raises in production unless the project sets it.

## Why

The provider id is stable and lowercase, which is how django-easy-icons keys its names. The display
name can carry capitals and spaces, and allauth may change it. Which icon set a project draws from
is the project's choice, and allauth supports far more providers than any package could keep
brand assets for. Shipping icons would turn this package into a brand-asset catalogue that goes
stale. Checking for them would repeat, and eventually contradict, django-easy-icons' own handling
of a missing name.

## Revisit if

allauth stops giving its provider element a provider id, or django-mvp's `<c-icon>` stops passing
its name straight to django-easy-icons.
