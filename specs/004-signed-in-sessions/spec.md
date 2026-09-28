# Feature Specification: Signed-in sessions

**Feature Branch**: `004-signed-in-sessions`

**Created**: 2026-09-26

**Status**: Draft

**Serves**: G1, a person can manage their account through an integrated authentication package,
and knowing where they are signed in is part of that. G2, the sessions page looks like part of the
host project. G3, the page, its menu entry and its card appear only when the project has installed
allauth's user sessions app.

**Roadmap**: R4, signed-in sessions

**Issue**: #8

**Depends on**: #5, which reskins the account management pages and adds the Account Center entries
and cards this feature adds to.

**Input**: A person sees every browser and device signed in to their account, with the current one
marked, and signs out every other session at once, for example after losing a phone or using a
shared computer. The package reskins allauth's user sessions page the same way it reskins the
account app: templates where allauth looks for them, no configuration, no checks, and no runtime
dependency on the user sessions app.

## Clarifications

### Session 2026-09-26

- Q: Can a person sign out one chosen session rather than all the others? → A: No. allauth's
  browser page signs out every session except the current one, and signing out a single chosen
  session exists only in allauth's headless API. Under Article XII, upstream does the work, so
  that gap is raised with allauth rather than built here, and this feature offers what the page
  offers.
- Q: What does each session show, to tell them apart? → A: What allauth records: when the session
  started, the IP address it came from, and the browser's user-agent string as allauth stores it.
  The package does not turn the user-agent into a friendlier name, because allauth does not.
- Q: When is "Last seen" shown? → A: Only when the project turns on allauth's activity tracking,
  which the package leaves to the project. The demo turns it on so the column can be seen.
- Q: Where does the sessions page appear? → A: As a "Sessions" entry and card in the Account
  Center, added the same way as the other account management pages (ADR 0002). Both appear whenever
  allauth routes its sessions page.
- Q: How does the sessions table behave on a phone? → A: Every column stays readable. If the table
  is wider than the screen it scrolls sideways inside its own area, and the page itself does not.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See where you are signed in (Priority: P1)

A signed-in person opens "Sessions" from the Account Center. They see a table of every browser and
device signed in to their account: when each session started, the IP address it came from and the
browser it reported, with the one they are using marked "Current". If the project tracks activity,
each row also shows when that session was last seen. The page looks like the rest of account
management.

**Why this priority**: A person cannot decide whether to sign anything out until they can see what
is signed in, and the list is useful on its own for checking nothing unexpected is there.

**Independent Test**: Signed in to the demo as a person with several sessions, open the Account
Center, follow "Sessions", and check the page lists each session with its start time, IP address,
browser and last-seen time, marks the current one, and renders as an account management page.

**Acceptance Scenarios**:

1. **Given** a signed-in person, **When** they open the Account Center, **Then** it has a
   "Sessions" entry and card that lead to the sessions page.
2. **Given** a project without allauth's user sessions app installed, **When** the Account Center
   renders, **Then** it has no sessions entry or card, and nothing raises.
3. **Given** a person signed in from three browsers, **When** they open the sessions page, **Then**
   it lists all three, with the current one marked "Current".
4. **Given** a project with activity tracking turned on, **When** the sessions page renders,
   **Then** each session shows when it was last seen. **Given** tracking is off, **Then** there is
   no last-seen column.
5. **Given** a phone-width screen, **When** the sessions page renders, **Then** every column can be
   read, and only the table scrolls sideways, never the page.

---

### User Story 2 - Sign out every other session (Priority: P1)

From the sessions page, a person who is signed in somewhere else presses allauth's "Sign Out Other
Sessions". Every session except the one they are using ends, allauth's confirmation appears, and
the page now lists only the current session. With only the current session left, the button becomes
allauth's plain "Sign Out", which signs them out of this browser.

**Why this priority**: Ending sessions they no longer control is the reason the page exists, for
example after losing a phone or leaving a shared computer signed in.

**Independent Test**: In the demo, sign in as a person with several sessions, open the sessions
page, press "Sign Out Other Sessions", and check the confirmation appears in the shell, only the
current session remains, and the button now reads "Sign Out" and leads to the sign-out page.

**Acceptance Scenarios**:

1. **Given** a person with sessions in three browsers, **When** they press "Sign Out Other
   Sessions", **Then** the other two sessions end and the page lists only the current one.
2. **Given** the other sessions have just been signed out, **When** the page renders, **Then**
   allauth's "Signed out of all other sessions." message appears in the shell.
3. **Given** a browser whose session was signed out, **When** it next requests a page, **Then** it
   is no longer signed in.
4. **Given** a person with only the current session, **When** the sessions page renders, **Then**
   its button reads "Sign Out", and pressing it signs them out through the site's own sign-out page.

---

### Edge Cases

- A session started before the project installed allauth's user sessions app is not listed until
  allauth records it: at that browser's next sign-in, or on its next request when activity tracking
  is on.
- A session with no recorded IP address or user-agent still gets its row, with that cell left
  empty.
- A host project that already overrides allauth's sessions template keeps its own.
- allauth asks for no confirmation before signing out the other sessions, and neither does the
  reskinned page. The current session is never among those signed out.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: allauth's sessions page MUST render inside the host project's application shell and
  theme, as an account management page with the shell's navigation, once this package and
  `allauth.usersessions` are installed.
- **FR-002**: Each session on the page MUST show when it started, its IP address and its browser as
  allauth records them, and the current session MUST be marked "Current".
- **FR-003**: The page MUST show when each session was last seen if the project has turned on
  allauth's activity tracking, and MUST NOT show the column otherwise.
- **FR-004**: The Account Center MUST show a "Sessions" entry and card when allauth routes its
  sessions page, and neither otherwise.
- **FR-005**: Signing out the other sessions MUST use allauth's own form and action, and allauth's
  confirmation message MUST be visible on the rendered page.
- **FR-006**: With only the current session left, the page MUST offer allauth's "Sign Out", which
  leads to the site's own sign-out page.
- **FR-007**: Every column of the sessions table MUST be readable at phone width, with the table
  scrolling sideways inside its own area rather than the page scrolling.
- **FR-008**: The package MUST NOT declare the user sessions app as a runtime dependency, set any
  of its settings, or check how it is configured.
- **FR-009**: The demo MUST install the user sessions app with activity tracking on, and give one
  seeded account several sessions, so the list, the current marker and "Sign Out Other Sessions"
  can all be seen.
- **FR-010**: The README MUST say how a project turns the sessions page on, that only sessions
  allauth has recorded are listed, and that signing out one chosen session is not offered.
- **FR-011**: Every string the package adds MUST be marked for translation.
- **FR-012**: `CONTEXT.md` MUST define signed-in session: one browser or device where a person is
  currently signed in to their account.

### Traceability

| Requirement | Story |
|---|---|
| FR-002, FR-003, FR-004, FR-007, FR-012 | US1 |
| FR-005, FR-006 | US2 |
| FR-001, FR-008, FR-009, FR-010, FR-011 | US1, US2 |

### Key Entities

- **Signed-in session**: one browser or device where a person is currently signed in to their
  account. allauth records when it started, its IP address and its browser, and when it was last
  seen if activity tracking is on (`CONTEXT.md`).
- **Current session**: the signed-in session belonging to the browser the person is using now.
  "Sign Out Other Sessions" never ends it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The sessions page renders inside the shell in the demo, and a test fails if it falls
  back to allauth's bare markup.
- **SC-002**: A person with sessions in several browsers can find the sessions page from the
  Account Center, tell the current session from the others, and sign the others out without
  leaving the site's pages.
- **SC-003**: After "Sign Out Other Sessions", no browser other than the current one is still
  signed in to that account.
- **SC-004**: At phone width, every column of the sessions table can be reached and the page itself
  does not scroll sideways.
- **SC-005**: With the user sessions app absent, the Account Center has no sessions entry or card
  and no page raises.

## Assumptions

- FS-001 is delivered. Its reskinned layouts, elements and Account Center wiring are what this
  feature adds to. allauth draws the sessions list with table elements FS-001 did not need, so this
  feature reskins those.
- FS-003 adds its own Account Center entry and card and is not yet built. Neither feature depends on
  the other, and each adds to the Account Center without changing the other's entries.
- allauth's user sessions app keeps rendering through its layout and element templates across the
  65.x line.
- Installing the user sessions app, adding its middleware and turning on activity tracking belong
  to the host project.
- Signing out one chosen session is an upstream gap in allauth's browser pages. Raising it there is
  the maintainer's decision, and building it here would need an ADR.
