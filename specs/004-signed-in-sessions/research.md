# Research — 004 Signed-in sessions

Every claim about allauth cites the installed package, django-allauth 65.19.4, under
`.venv/lib/python3.13/site-packages/allauth/`. Paths below are relative to that directory unless
they start with `mvp_accounts/`, `demo/` or `tests/`.

## R1 — What the sessions page renders, and what it extends

allauth routes the page at `sessions/` under its URLconf, named `usersessions_list`, only when
`allauth.usersessions` is installed (`urls.py:71`). The view is `ListUserSessionsView`
(`usersessions/views.py`), a login-required `FormView` over `usersessions/usersession_list.html`.

That template extends `usersessions/base_manage.html`, which is one line,
`{% extends "allauth/layouts/manage.html" %}`. FS-001 already overrides that layout
(`mvp_accounts/templates/allauth/layouts/manage.html`), so the page renders inside the Account
Center shell with no page template of its own. FR-001 is met by FS-001's layout, and this
feature's work on the page is its elements and tests.

The page draws, through elements:

| Element | Tags | Overridden today |
|---|---|---|
| `h1` | `usersessions,list` | yes (FS-001) |
| `form` | `sessions`, `no_visible_fields=True`, a `body` and an `actions` slot | yes (FS-001) |
| `table`, `thead`, `tbody`, `tr`, `th`, `td` | `table` gets `sessions` | **no** |
| `badge` | `session,current` | yes (FS-001) |
| `button` | `type="submit"`, no tags | yes (FS-001) |

allauth's bare `table` element is `<table>` with its slot and nothing else, and its `thead` to `td`
are the same shape. They are the only elements on the page this package does not draw yet.

The header row has three cells, four with activity tracking, and every body row has one more: the
last cell holds the "Current" badge or nothing. That is allauth's markup and the package keeps it.

The template loads `humanize` for `naturaltime`, so `django.contrib.humanize` must be installed for
the page to render at all. That is a requirement of allauth's page on the host project, not
something this package adds or checks.

## R2 — The table elements, shared with FS-003

FS-003 (`003-two-factor-pages`, open as PR #28, not merged) overrides the same six table elements
for the security-key list. Its `table` wraps the table in `<div class="overflow-x-auto">` with
django-mvp's `table` class, which is exactly what FR-007 and decision D3 ask for: the table scrolls
sideways inside its own area and the page does not.

This feature adds the same six files with **byte-identical content** to FS-003's. Whichever of the
two branches merges second then carries an identical addition, which git merges without a conflict,
and the sessions page and the security-key list are drawn by one set of elements rather than two
that could drift. Both `overflow-x-auto` and `table` are in django-mvp's prebuilt stylesheet
(`mvp/static/css/django-mvp.css`), so the classes take effect.

## R3 — Sessions, the current marker and signing out

`UserSession` (`usersessions/models.py:88`) records `created_at`, `ip`, `user_agent`,
`last_seen_at` and the `session_key`. allauth writes one on every sign-in
(`usersessions/signals.py`, `on_user_logged_in`) and, with `USERSESSIONS_TRACK_ACTIVITY` on, on
every request through `allauth.usersessions.middleware.UserSessionsMiddleware`.

The list view calls `purge_and_list`, which drops any `UserSession` whose Django session no longer
exists (`models.py:27-33`). A seeded or test session therefore needs a real row in Django's session
store, not a `UserSession` alone, or it is purged before the page draws it.

`show_last_seen_at` is `USERSESSIONS_TRACK_ACTIVITY`, read through `get_setting` at request time,
so `override_settings` turns the column on and off in a test.

The form posts to `usersessions_list` when there are two or more sessions, and its view ends every
session except the current one (`usersessions/internal/flows/sessions.py`, `end_other_sessions`),
then adds `usersessions/messages/sessions_logged_out.txt`, "Signed out of all other sessions.", and
redirects back to the list. With one session, the form posts to `account_logout` and the button
reads "Sign Out", which signs the person out through the site's own sign-out view.

The shell draws Django's messages on every page, so the confirmation appears without a template of
this package's.

## R4 — Account Center entry and card

The same pattern as FS-001 and FS-002, recorded in ADR 0002: a `MenuItem` in the "Account" group
with `view_name="usersessions_list"`, which django-mvp drops from the rendered menu when the name
does not resolve, and a card in `mvp/account/overview.html` drawn inside
`{% url "usersessions_list" as sessions_url %}{% if sessions_url %}`. Neither checks settings or
whether the app is installed (FR-004, FR-008).

Icon: django-mvp's Bootstrap pack has no device or session icon. `login`
(`bi-box-arrow-in-right`) is the one that reads as "where you are signed in", and it is in the
pack, so the demo needs no icon of its own.

## R5 — Tests

- Sessions for a test are real Django sessions: sign a client in (`force_login` saves a session)
  and create its `UserSession` from the session key, or build further sessions with
  `SessionStore` so `purge_and_list` keeps them. One factory, `UserSessionFactory`, owns that.
- Three browsers are three `Client` instances signed in as the same account. After "Sign Out Other
  Sessions" on one, the other two are answered by the Account Center with a redirect to sign-in
  (SC-003).
- Without the app: a subprocess with `settings_without_usersessions.py`, the suite's settings with
  `allauth.usersessions` and its middleware removed, as FS-002 did for the social account app.

## R6 — The demo

`allauth.usersessions` after `allauth.socialaccount`, `django.contrib.humanize`, the middleware
after `AccountMiddleware`, and `USERSESSIONS_TRACK_ACTIVITY = True`. `seed_demo` gives
`regular.user@example.com` two further sessions with fixed IP addresses, user-agents and start
times, each backed by a Django session, so signing in as that account shows three with the
browser's own marked "Current". Signed in as any other seeded account, the page shows one session
and the "Sign Out" button, so both button states are reachable. The seeded sessions are replaced on
each run, so "Sign Out Other Sessions" can be tried, and seeded again.
