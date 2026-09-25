# Roadmap — django-mvp-accounts

**Date:** 2026-09-24

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md)
for domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| `0.1.0` | All Essential goals delivered. The minimum usable release, and the first publish |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes |
| `1.0.0` | All Expected goals delivered. The complete, dependable release |
| `1.x` | Stable line: fixes and additive features only |
| `2.0` | The next major, where breaking changes go |

A goal is not one minor release: some take several, and one release can move
two. Once `1.0` ships, a breaking change never goes out as `1.x`. It waits for
the next major.

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — Accounts, sign-in and recovery

*feature · advances G1, G2, G3*

A person can create an account on a django-mvp site, sign in, sign out, get
back in after forgetting their password, and change the details of their
account, all on pages that belong to the site. This comes first because
everything else on the roadmap is a page inside an account that already exists:
two-factor authentication, connected social accounts, session management and
API tokens all assume someone is signed in and has somewhere to manage their
account from.

It is built on allauth's account app, the first authentication package this
package supports.

**Deliverables:**

- Sign-up, sign-in, sign-out, password reset and email verification pages,
  rendered as the site's own entrance pages rather than allauth's bare ones.
- Pages for managing email addresses and changing or setting a password,
  reachable from one place in the application shell once signed in.
- An account-management menu entry and landing page that list only what the
  project has installed, so later items add to it without reorganising it.
- Every behaviour allauth's account app offers that the project turns on in its
  own settings is presented, including passwordless sign-in by emailed code and
  re-authentication before a sensitive change.
- Adoption documented in the README: what to install, what to add to
  `INSTALLED_APPS` and the URL configuration, and nothing more than that.

Serves G1, G2 and G3. Out of scope: social sign-in, two-factor authentication,
session management and API tokens, which follow as their own items.

## Expected goals: v1.0.0

Everything needed for the complete release.

### R2 — Connected social accounts

*feature · advances G1, G2, G3*

A person can sign up and sign in with an external account such as GitHub or
Google, and connect or disconnect those accounts from their own account pages.
Built on allauth's social account app.

**Deliverables:**

- A button for each configured provider on the sign-in and sign-up pages, and
  none for a provider the project has not configured.
- The extra sign-up step allauth needs when an external account is missing
  something, rendered as an entrance page.
- A page listing the person's connected accounts, where they can connect
  another or disconnect one.

Serves G1, G2 and G3. Out of scope: configuring providers, which stays in the
host project's settings.

### R3 — Two-factor authentication

*feature · advances G1, G2, G3*

A person can protect their account with a second factor: an authenticator app,
recovery codes, and security keys or passkeys where the project enables them.
Built on allauth's multi-factor authentication app.

**Deliverables:**

- Pages for setting up, viewing and removing each second factor the project
  enables.
- The second-factor challenge during sign-in, rendered as an entrance page.
- Recovery codes that can be viewed, downloaded and regenerated.

Serves G1, G2 and G3.

### R4 — Signed-in sessions

*feature · advances G1, G2, G3*

A person can see every device and browser currently signed in to their
account, and sign any of them out. Built on allauth's user sessions app.

**Deliverables:**

- A page listing the person's active sessions, with enough detail to recognise
  each one and the current session marked.
- Signing out one session, or every session except the current one.

Serves G1, G2 and G3.

### R5 — Personal API tokens

*feature · advances G4, G2, G3*

When the project has a REST API built on Django REST framework, a person can
create tokens to reach it, see the tokens they have, and revoke any of them.
Built on django-rest-knox, which, unlike Django REST framework's own token
model, allows several tokens per person, lets them expire, and does not store
them in a form that can be read back.

**Deliverables:**

- A page where a person creates a token, sees it once at creation, and lists
  and revokes the tokens they already have.
- Tokens created there authenticate requests to the project's API.
- Nothing at all in a project without Django REST framework: no menu entry, no
  page and no import error.

Serves G4, G2 and G3. Out of scope: tokens issued to third-party applications
on a person's behalf, which is OAuth.

### R6 — Tested against current releases

*resolve · advances G5*

Every integrated package is tested against its latest release, so a new
release that breaks something is found here before a project finds it.

Serves G5.
