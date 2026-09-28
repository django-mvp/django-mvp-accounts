# Decisions — 004 Signed-in sessions

## D1 — Only "sign out other sessions", not one chosen session

The issue and R4 both say a person can sign out any session. allauth's browser page offers one
action, which ends every session except the current one. Ending a single chosen session exists only
in allauth's headless API. Article XII says a feature upstream lacks is raised there first, and
building it here is an ADR. The spec therefore delivers what allauth's page does and records
single-session sign-out as an upstream gap for the maintainer to raise.

**ADR:** none — nothing is built. Single-session sign-out is left to allauth, and an ADR is needed only if this package ever builds it.

## D2 — The browser column shows allauth's raw user-agent

A user-agent string is hard to read, and turning it into "Firefox on macOS" would help a person
recognise a session. allauth shows the raw string and has no parser, and adding one here would be a
feature allauth does not have. The column shows what allauth records.

**ADR:** none — the package shows what allauth records and adds no behaviour of its own.

## D3 — The table scrolls, the page does not

allauth's list has up to five columns (started, IP address, browser, last seen, current marker),
more than a phone screen fits. Hiding a column would hide information a person needs to recognise a
session, so the table keeps every column and scrolls sideways inside its own area.

**ADR:** none — the table elements FS-003 already defines do this. Nothing new is designed here.

## D4 — FS-004 read against FS-002, delivered since this spec landed

FS-002 merged after this specification. Read side by side, the two do not contradict each other.
Both add their own Account Center entry and card, and neither changes the other's behaviour, so
the plan builds FS-004 as specified.

**ADR:** none — a check made once before planning, nothing downstream inherits it.

## D5 — The table elements are FS-003's, added byte-for-byte

FS-003, open and not merged, adds the same six table elements for its security-key list, and its
`table` already scrolls sideways inside its own area as D3 asks. This branch starts from main
without FS-003, so it adds the same six files with identical content. Whichever branch merges
second carries an identical addition and merges without a conflict, and one set of elements draws
both tables.

**ADR:** none — the elements are templates allauth defines. Nothing here is a new design choice.

## D6 — "Sessions" uses the `login` icon

django-mvp's icon pack has no device or session icon. `login` is in the pack and reads as "where
you are signed in", so the entry and the card need no icon from the host project.

**ADR:** none — local to one menu entry and one card.

## D7 — The demo seeds two extra sessions for regular.user only

Signed in as regular.user, the sessions page lists three sessions and offers "Sign Out Other
Sessions". Signed in as any other seeded account, it lists one and offers "Sign Out". Each seeded
session is backed by a real Django session, because allauth drops any recorded session whose
Django session is gone before it draws the list. `seed_demo` replaces them on every run, so
signing out the others can be tried more than once.

**ADR:** none — demo data, never distributed.

## D8 — A session with no IP address cannot occur

The spec's edge cases include a session with no recorded IP address. allauth stores the address in
a required field and refuses to record a session without one, so no such row is ever written. The
edge case holds for the user-agent, which can be empty, and the tests cover that half.

**ADR:** none — a fact about allauth, nothing is designed here.

## D9 — Design review, one round, approved

Four findings, all applied to the plan: client-backed sessions come from allauth's middleware and
are told apart by each client's own address and browser (DR-001, research R5, T005, T009); the
no-IP edge case is unreachable (DR-002, D8); demo sessions are seeded after the password is set and
ended rather than deleted (DR-003, T007); T011 no longer repeats T009's sign-out check (DR-004).

**ADR:** none — plan corrections, local to this feature.

## D10 — The seeded sessions are keyed by their fixed IP addresses

**Decision:** `seed_demo` finds its earlier sessions for regular.user by the two fixed IP addresses and ends them with `UserSession.end()` before creating two new ones.
**Why:** a real sign-in by regular.user has another address, so it is left alone, and `end()` removes the Django session as well as the row.
**Revisit if:** a second seeded account needs sessions, or a sign-in from one of those documentation addresses becomes possible.

**ADR:** none — demo data, never distributed.

## D11 — The startup test lists the Sessions entry

`tests/test_apps.py` pins the Account group's children by name, so adding the Sessions entry
(FR-004) makes it list five. The expected list gains `"sessions"` at the end, and nothing else in
the test changes. FS-003 makes the same one-line edit for its own entry.

**ADR:** none — a test tracking a specified menu entry.

## D12 — Code review, one round, approved

Three low findings, all fixed: `seed_demo` reads the session store from `SESSION_ENGINE`, as allauth
and the test factory do (COR-002); its docstring says the seeded sessions expire after two weeks and
a re-run restores them (COR-001); a test pins that a hostile browser string renders as text, and
fails when the cell is marked safe (SEC-001). The middleware comment in the demo settings now says
it acts only with tracking on.

**ADR:** none — review fixes, local to this feature.
