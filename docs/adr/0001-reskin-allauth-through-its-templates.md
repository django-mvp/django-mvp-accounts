# ADR 0001 — Reskin allauth through its layout and element templates

**Status:** accepted

## Decision

The package puts allauth's pages inside the django-mvp shell by shipping templates under the
names allauth looks up, and does nothing else at runtime:

- `allauth/layouts/entrance.html` extends `mvp/entrance.html`, and `allauth/layouts/manage.html`
  extends the Account Center's `mvp/account/base.html`. `allauth/layouts/base.html` sends anything
  that extends it directly to the entrance layout.
- `allauth/elements/*.html` rebuild the elements allauth's account pages use from django-mvp's
  components. A whole form goes through `<c-form.render>`.
- `account/base_entrance.html` picks its layout by whether the visitor is signed in: management
  when signed in, entrance otherwise. An entrance page is one seen before signing in.
- A page allauth files under the wrong base for that rule is copied with only its parent changed.
  Today that is `account/logout.html` and `account/verified_email_required.html`. Each copy names
  the allauth version it came from.

allauth is a development dependency. The package declares no runtime dependency on it, sets none
of its settings and adds no checks about how a project configured it. A project lists
`mvp_accounts` ahead of `allauth` and `mvp` in `INSTALLED_APPS` so these templates win.

## Why

Every page in allauth's account app extends one of two layouts and draws its markup through a
small set of elements, so overriding those moves every page at once, including pages a later
release adds. Overriding each page template instead would mean about thirty copies of allauth's
markup to keep in step with every release, and forms replacing allauth's own are what the
constitution's Article XIII rules out.

Keeping allauth out of the runtime dependencies means a project that does not want accounts from
allauth never installs it, and a project that does already has it. The templates are only ever
loaded by allauth's views.

Choosing the layout by who is looking settles re-authentication and phone verification with one
line: allauth builds them on its entrance base, but a person changing their phone number is signed
in and belongs in account management. Sign-out and "verified email required" are the two pages
the rule gets wrong for this package's purposes, and they are small enough to copy.

## Revisit if

allauth stops rendering its account pages through `allauth/layouts/` and `allauth/elements/`, or
moves one of the copied pages onto a different base in a supported release.
