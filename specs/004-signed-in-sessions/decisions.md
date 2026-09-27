# Decisions — 004 Signed-in sessions

## D1 — Only "sign out other sessions", not one chosen session

The issue and R4 both say a person can sign out any session. allauth's browser page offers one
action, which ends every session except the current one. Ending a single chosen session exists only
in allauth's headless API. Article XIII says a feature upstream lacks is raised there first, and
building it here is an ADR. The spec therefore delivers what allauth's page does and records
single-session sign-out as an upstream gap for the maintainer to raise.

## D2 — The browser column shows allauth's raw user-agent

A user-agent string is hard to read, and turning it into "Firefox on macOS" would help a person
recognise a session. allauth shows the raw string and has no parser, and adding one here would be a
feature allauth does not have. The column shows what allauth records.

## D3 — The table scrolls, the page does not

allauth's list has up to five columns (started, IP address, browser, last seen, current marker),
more than a phone screen fits. Hiding a column would hide information a person needs to recognise a
session, so the table keeps every column and scrolls sideways inside its own area.

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
