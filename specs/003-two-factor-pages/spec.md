# Feature Specification: Two-factor authentication

**Feature Branch**: `003-two-factor-pages`

**Created**: 2026-09-26

**Status**: Draft

**Serves**: G1, a person can sign in and manage their account through an integrated authentication
package. G2, every entrance and account page looks like part of the host project. G3, what appears
depends on what the project has installed and enabled.

**Roadmap**: R3, two-factor authentication

**Issue**: #7

**Depends on**: #5, which reskins the account app's pages, form elements and the Account Center
entries this feature adds to.

**Input**: A person protects their account with a second factor: an authenticator app, recovery
codes, and security keys or passkeys where the project enables them. They set these up, change or
remove them from their account management pages, and use them when signing in. The package reskins
allauth's multi-factor app the same way it reskins the account app: templates where allauth looks
for them, no configuration, no checks, and no runtime dependency on allauth.

## Clarifications

### Session 2026-09-26

- Q: Which second factors get pages? → A: Whichever ones the project enables in allauth: the
  authenticator app, recovery codes, and security keys and passkeys. A factor the project has not
  enabled shows nothing, because allauth renders nothing for it.
- Q: Where does two-factor authentication appear in account management? → A: As an entry and a
  card in the Account Center, added the same way FS-001 adds its management pages. It appears
  whenever allauth routes its two-factor page.
- Q: Which pages are entrance pages? → A: The second-factor step during sign-in, the "trust this
  browser" prompt, and sign-up by passkey, because each is seen before the person is fully signed
  in. The rest are account management pages. Re-authentication with a second factor follows
  FS-001's rule for re-authentication and renders as an account management page.
- Q: What keeps the security-key and passkey pages working after the reskin? → A: allauth's
  JavaScript for those pages finds its buttons, hidden inputs and forms by the ids and data
  attributes allauth's templates give them. Every reskinned element keeps each id and attribute
  allauth passes it, so the script finds the same hooks it finds on allauth's own markup.
- Q: How does the authenticator-app QR code stay readable in a dark theme? → A: It is always shown
  dark on a light background, whatever the theme, because authenticator apps cannot reliably read
  an inverted code.
- Q: Can the security-key and passkey pages be tried through the dev server's tailnet address?
  → A: They render there, but browsers only allow security keys and passkeys over HTTPS or on
  `localhost`, so adding or using one fails on a plain HTTP address. The tests cover rendering and
  the script hooks. Setting up HTTPS for the dev server is outside this feature.
- Q: What about the notification emails allauth sends when a factor is added or removed? → A: They
  keep allauth's own templates, as in FS-001.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Protect an account with an authenticator app and recovery codes (Priority: P1)

A signed-in person opens "Two-factor authentication" from the Account Center. They set up an
authenticator app by scanning allauth's QR code or typing its key, and confirming a code. They view,
download and regenerate their recovery codes, and can turn the authenticator app off again. Every
page looks like the rest of account management.

**Why this priority**: An authenticator app with recovery codes is the second factor nearly every
project enables first, and it works on any address, with no special hardware.

**Independent Test**: Signed in to the demo, open the Account Center, follow "Two-factor
authentication", set up the authenticator app with a generated code, view and download the
recovery codes, generate a new set, and turn the app off. Every page renders as an account
management page with allauth's forms and messages.

**Acceptance Scenarios**:

1. **Given** a signed-in person, **When** they open the Account Center, **Then** it has a
   "Two-factor authentication" entry and card.
2. **Given** a project without the multi-factor app installed, **When** the Account Center renders,
   **Then** it has no two-factor entry or card, and nothing raises.
3. **Given** a person setting up the authenticator app, **When** the page renders in a dark theme,
   **Then** the QR code is dark on a light background, and the manual key is shown beside it.
4. **Given** a person who enters a wrong code, **When** they submit, **Then** allauth's error appears
   next to the code field.
5. **Given** a person with recovery codes, **When** they view, download or regenerate them, **Then**
   each page renders as an account management page, and the download is allauth's file.
6. **Given** a project that has not enabled the authenticator app, **When** the two-factor page
   renders, **Then** nothing on it offers one.

---

### User Story 2 - Pass the second-factor step when signing in (Priority: P1)

A person with a second factor signs in with their password and then meets allauth's second-factor
step. They enter a code from their authenticator app, use a recovery code, or use a security key,
depending on what they have set up. If the project offers it, they are asked whether to trust this
browser. Before a sensitive change, allauth may ask for a second factor again. Each page looks like
the site's other pages of its kind.

**Why this priority**: Setting a second factor up is pointless if the step that uses it breaks or
looks foreign, and a person meets it on every sign-in.

**Independent Test**: In the demo, sign in as a person with an authenticator app set up, pass the
second-factor step with a code, answer the "trust this browser" prompt, then trigger
re-authentication and pass it with a code. The sign-in pages render as entrance pages and
re-authentication renders as an account management page.

**Acceptance Scenarios**:

1. **Given** a person with an authenticator app, **When** they sign in with their password, **Then**
   the second-factor step renders as an entrance page with allauth's code form.
2. **Given** a person who has only recovery codes left, **When** they reach the step, **Then**
   allauth's form accepts a recovery code on the same page.
3. **Given** a project that offers "trust this browser", **When** the person passes the step,
   **Then** the prompt renders as an entrance page.
4. **Given** allauth asks for a second factor before a sensitive change, **When** that page
   renders, **Then** it renders as an account management page with allauth's form.

---

### User Story 3 - Use security keys and passkeys (Priority: P2)

With security keys enabled, a signed-in person adds a security key or passkey, gives it a name,
renames it and removes it. With passkey sign-in enabled, the sign-in page offers signing in with a
passkey instead of a password. With passkey sign-up enabled, a new visitor creates an account with
a passkey. allauth's JavaScript does the work on each of these pages, and the reskin keeps
everything it relies on.

**Why this priority**: It depends on the project enabling it and on HTTPS, so it matters to fewer
projects than the authenticator app, and everything else in this feature works without it.

**Independent Test**: With security keys, passkey sign-in and passkey sign-up turned on, render the
add, list, rename and remove pages, the sign-in page and the passkey sign-up page. Each renders as
its kind of page, and every id and data attribute allauth's script looks for is present on the
element allauth gave it to.

**Acceptance Scenarios**:

1. **Given** a person with two security keys, **When** they open the security-key list, **Then** it
   renders as an account management page listing both, with allauth's rename and remove actions.
2. **Given** a person adding a security key, **When** the add page renders, **Then** the button,
   hidden input and script configuration carry the same ids and data attributes as on allauth's
   own page.
3. **Given** a project with passkey sign-in enabled, **When** a visitor opens the sign-in page,
   **Then** it offers signing in with a passkey, and the form and script allauth uses for it carry
   their ids and data attributes.
4. **Given** a project with passkey sign-up enabled, **When** a visitor opens the passkey sign-up
   page, **Then** it renders as an entrance page with its script hooks intact.
5. **Given** a project that has not enabled security keys, **When** the two-factor page renders,
   **Then** nothing on it offers one.

---

### Edge Cases

- A host project that already overrides one of allauth's multi-factor templates keeps its own.
- Security keys and passkeys cannot be added or used on a plain HTTP address other than
  `localhost`. The pages still render, and allauth's script reports the browser's refusal.
- Removing the last second factor turns two-factor authentication off, and allauth's message saying
  so appears in the shell.
- Messages allauth adds after a factor is added, removed or regenerated appear in the shell like
  any other Django message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every page allauth's multi-factor app renders, and the account app's passkey sign-up
  page, MUST render inside the host project's application shell and theme once this package and
  `allauth.mfa` are installed.
- **FR-002**: The second-factor step during sign-in, the "trust this browser" prompt and passkey
  sign-up MUST render as entrance pages, without the shell's navigation.
- **FR-003**: The two-factor overview, authenticator-app, recovery-code, security-key and
  re-authentication pages MUST render as account management pages, with the shell's navigation.
- **FR-004**: The Account Center MUST show a "Two-factor authentication" entry and card when allauth
  routes its two-factor page, and neither otherwise.
- **FR-005**: Every element the package reskins MUST keep each id and data attribute allauth passes
  it, so allauth's JavaScript finds the same hooks as on allauth's own markup.
- **FR-006**: The authenticator-app QR code MUST render dark on a light background in every theme.
- **FR-007**: A page MUST show only what allauth renders for the factors the project has enabled.
- **FR-008**: Every error and message allauth reports on these pages MUST be visible on the
  rendered page.
- **FR-009**: The package MUST NOT declare the multi-factor app as a runtime dependency, set any of
  its settings, or check how it is configured.
- **FR-010**: The demo MUST enable the authenticator app, recovery codes, security keys, passkey
  sign-in, passkey sign-up and "trust this browser", so every page in this feature can be reached.
- **FR-011**: Every string the package adds MUST be marked for translation.
- **FR-012**: `CONTEXT.md` MUST define passkey: a security key or device credential that can also be
  used to sign in without a password, which allauth treats as one kind of authenticator.

### Traceability

| Requirement | Story |
|---|---|
| FR-003, FR-004, FR-006, FR-009, FR-010, FR-011 | US1 |
| FR-002 | US2 |
| FR-005, FR-012 | US3 |
| FR-001, FR-007, FR-008 | US1, US2, US3 |

### Key Entities

- **Second factor**: something a person has, besides their password, that proves who they are:
  an authenticator app, a recovery code, or a security key or passkey (`CONTEXT.md`).
- **Recovery codes**: single-use codes allauth generates as a fallback when a person cannot use
  their other factor.
- **Security key**: a hardware or device credential used as a second factor through the browser.
- **Passkey**: a security key or device credential that can also be used to sign in without a
  password. allauth treats both as one kind of authenticator.
- **Trusted browser**: a browser the person has told allauth not to ask for a second factor on for
  a while.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every multi-factor page, and passkey sign-up, renders inside the shell in the demo,
  and a test for each page fails if that page falls back to allauth's bare markup.
- **SC-002**: On every page that loads allauth's security-key script, every id and data attribute
  the script looks for is present, and a test fails if any is missing.
- **SC-003**: The QR code has a light background and dark modules in both the demo's light and dark
  themes.
- **SC-004**: A person can set up an authenticator app, sign in with it, and use a recovery code
  without leaving the site's pages.
- **SC-005**: With the multi-factor app absent, the Account Center has no two-factor entry or card
  and no page raises.

## Assumptions

- FS-001 is delivered first. Its reskinned layouts, elements and Account Center wiring are what this
  feature adds to, and any element attribute the multi-factor pages need that FS-001 does not yet
  forward is added to that element here.
- allauth's multi-factor app keeps rendering through its layout and element templates, and keeps
  its script hooks, across the 65.x line.
- The notification emails allauth sends keep allauth's own templates.
- Enabling factors and setting WebAuthn options belong to the host project.
