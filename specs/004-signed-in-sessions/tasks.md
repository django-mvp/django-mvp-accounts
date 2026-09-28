# Tasks — 004 Signed-in sessions

**Branch**: `004-signed-in-sessions` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it.

## Order

**US1 → US2, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — See where you are signed in (P1)

Issue: #25. Delivers FR-001 to FR-004, FR-007, FR-009, FR-012, US1's part of FR-008, FR-010 and
FR-011, and SC-001, SC-004, SC-005 and US1's part of SC-002.

### T001 — The user sessions app in the demo

**Files**: `demo/settings.py`, `tests/test_demo.py`

Research R1, R6. `allauth.usersessions` after `allauth.socialaccount` in `INSTALLED_APPS`, and
`django.contrib.humanize` after `django.contrib.staticfiles`, with a comment that allauth's
sessions page loads its date filters from it. `allauth.usersessions.middleware.UserSessionsMiddleware`
after `AccountMiddleware`. `USERSESSIONS_TRACK_ACTIVITY = True`, with a comment that the demo turns
it on so the last-seen column can be seen and that the package leaves it to the project. Test:
`usersessions_list` resolves in the demo.

### T002 — The table elements

**Files**: `mvp_accounts/templates/allauth/elements/table.html`, `thead.html`, `tbody.html`,
`tr.html`, `th.html`, `td.html`, `tests/test_elements.py`

Research R2. Copy the six files **byte-for-byte** from the `003-two-factor-pages` branch
(`git show origin/003-two-factor-pages:mvp_accounts/templates/allauth/elements/<name>.html`). Do
not reword their comments or reformat them: an identical addition is what lets both branches merge
without a conflict. Tests in `tests/test_elements.py`, rendering allauth's `{% element table %}`
with a head and body row: the table carries django-mvp's `table` class inside an `overflow-x-auto`
wrapper; `td` with `align="right"` gets `text-end` and without it gets no class.

### T003 — The Sessions entry

**Files**: `mvp_accounts/menus.py`, `tests/test_menus.py`

Research R4. One more child of the existing "Account" `MenuGroup`, after Connected accounts:
`MenuItem(name="sessions", view_name="usersessions_list", extra_context={"label": _("Sessions"),
"icon": "login"})`. Add "the sessions page without the user sessions app" to the module
docstring's list of what django-mvp leaves out when not routed. Test: the rendered Account Center
menu has "Sessions" inside the "Account" group.

### T004 — The Sessions card

**Files**: `mvp_accounts/templates/mvp/account/overview.html`, `tests/test_account_center.py`

Research R4. A card after the connected accounts card, resolved with `{% url "usersessions_list"
as sessions_url %}` and drawn only when it resolves, icon `login`, the sentence "See the browsers
and devices signed in to your account, and sign out the others." and a "Manage sessions" button.
Test: add "Sessions" to the module's `CARDS` table, and assert the card's button text and icon.

### T005 — The sessions page

**Files**: `tests/factories.py`, `tests/test_sessions_page.py`, `pyproject.toml`
(`non-mirror-paths`)

Research R1, R3, R5. `UserSessionFactory`: a `UserSession` for a user from `UserFactory`, whose
`session_key` is a saved `SessionStore` session carrying that user's id, backend and auth hash, so
allauth's `purge_and_list` keeps it; `ip`, `user_agent` and `created_at` overridable. It is only
for sessions no client holds. A signed-in client's own row is created by the demo's
`UserSessionsMiddleware` on its first request, and rewritten from each later request, so never
create a row for a client's session key by hand (it collides on the unique key). Build each client
with its own `REMOTE_ADDR` and `HTTP_USER_AGENT` defaults, sign it in with `force_login`, make one
request, and tell rows apart by those values (research R5). Tests, each asserting the plan's four
assertions as a management page:

- a person signed in from three clients, each with its own IP address and user-agent: all three
  sessions listed with those values, and exactly one "Current" badge, in the row for the client
  that asked (acceptance scenario 3);
- with tracking on (the demo's setting): the "Last seen at" header and a last-seen cell per row;
  under `override_settings(USERSESSIONS_TRACK_ACTIVITY=False)`: no "Last seen at" (scenario 4);
- the table is inside the `overflow-x-auto` wrapper and carries the `table` class, so it scrolls
  inside its own area (FR-007, SC-004);
- a factory session with `user_agent=""` still has its row, with an empty cell (edge case);
- a host template at `usersessions/usersession_list.html` placed ahead of the package's wins, as
  the existing host-override test does for the sign-in page (edge case);
- the page falls back to allauth's bare markup if FS-001's manage layout is absent: probe by
  removing it locally and confirm the tests fail, then restore (SC-001; record the probe in the
  story report, do not commit it).

### T006 — Without the user sessions app

**Files**: `tests/settings_without_usersessions.py`, `tests/test_without_usersessions.py`,
`pyproject.toml` (`non-mirror-paths`)

Research R5. Settings from the suite's with `allauth.usersessions` **and**
`allauth.usersessions.middleware.UserSessionsMiddleware` removed, allauth kept. The middleware has
to go too: importing it imports `usersessions.models`, which raises `ImproperlyConfigured` when
the app is absent. A subprocess through the runner `test_without_socialaccount.py` already shares: the
Account Center and its landing page render with 200, "Sessions" is in neither the menu nor the
cards, and nothing raises (acceptance scenario 2, SC-005).

### T007 — Seeded sessions in the demo

**Files**: `demo/management/commands/seed_demo.py`, `tests/test_demo.py`

Research R6. `seed_demo` gives `regular.user@example.com` two further sessions, each a saved
Django session carrying that user's id, backend and hash, and a `UserSession` with a fixed IP
address (`192.0.2.10`, `198.51.100.24`), a realistic fixed user-agent (a phone browser and a
desktop one) and a start time some days back. Seed them in `seed_states`, after the account loop has
set the password, from the saved user's `get_session_auth_hash()`: `set_password` changes the hash,
and allauth drops any session whose hash no longer matches. Each run first ends the sessions it
seeded before (that user's `UserSession`s with those IP addresses) with `UserSession.end()`, not
`delete()`, so their Django sessions go too. Running it twice leaves two, and signing the others
out can be tried again. Never print a session key. The docstring and closing output say regular.user has sessions in
two other browsers and that any other account shows a single session. Test: running `seed_demo`
twice leaves exactly two seeded sessions for regular.user, both kept by `purge_and_list`.

### T008 — Documentation, glossary and catalogue

**Files**: `README.md`, `CONTEXT.md`, `CHANGELOG.md`, `mvp_accounts/locale/en/LC_MESSAGES/django.po`

FR-010 to FR-012. A README section on signed-in sessions: install `allauth.usersessions`, its
middleware and `django.contrib.humanize` as allauth documents; turn on
`USERSESSIONS_TRACK_ACTIVITY` for the last-seen column; only sessions allauth has recorded are
listed (a browser signed in before the app was installed appears after its next sign-in, or its
next request with tracking on); signing out one chosen session is not offered, only every other
session at once. Add Sessions to the README's Account Center list, saying it appears only with the
user sessions app installed. `CONTEXT.md`: "Signed-in session — one browser or device where a
person is currently signed in to their account." `makemessages -l en` from inside `mvp_accounts/`.
CHANGELOG `Added` entry under `[Unreleased]`.

---

## US2 — Sign out every other session (P1)

Issue: #26. Delivers FR-005, FR-006, US2's part of FR-001, FR-008 to FR-011, SC-003 and US2's part
of SC-002.

### T009 — Signing out the others

**Files**: `tests/test_sessions_page.py`

Research R3, R5. Three clients signed in as one person, each with its own `REMOTE_ADDR` and
`HTTP_USER_AGENT` and each having made one request, so each has its `UserSession` (T005). Tests:

- the page's button reads "Sign Out Other Sessions" and its form posts to `usersessions_list`;
- posting from one client (following the redirect) lists only that client's session, and
  allauth's "Signed out of all other sessions." is in the shell's messages on the page it lands on
  (scenarios 1 and 2, FR-005);
- the other two clients are sent to sign in by the Account Center afterwards (scenario 3, SC-003);
- the posting client is still signed in.

### T010 — Signing out the last session

**Files**: `tests/test_sessions_page.py`

Research R3. A person with one session: the button reads "Sign Out" and the form posts to
`account_logout`; posting it signs them out, and the Account Center then sends them to sign in
(scenario 4, FR-006).

### T011 — The demo walk-through and documentation

**Files**: `tests/test_demo.py`, `README.md`, `CHANGELOG.md`

FR-009. Test: after `seed_demo`, a client that signs in as regular.user with its password sees
three sessions and "Sign Out Other Sessions". README's sessions section says the page signs out
every session but the current one without asking first, as allauth's does. Extend the CHANGELOG
entry if US1's does not already cover signing out.
