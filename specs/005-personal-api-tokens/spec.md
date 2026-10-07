# Feature Specification: Personal API tokens

**Feature Branch**: `005-personal-api-tokens`

**Created**: 2026-10-07

**Status**: Draft

**Serves**: G4, when the project has a REST API a person can create, see and revoke their own API
tokens. G2, the tokens page looks like part of the host project. G3, the page, its menu entry and
its card appear only in a project that has installed the token package and routed the page.

**Roadmap**: R5, personal API tokens

**Issue**: #35

**Depends on**: #5, delivered, which put the account management pages in django-mvp's Account
Center. The tokens page is one more of them.

**Input**: When a project has a REST API built on Django REST framework, a person creates API
tokens for reaching it from their account pages, sees which tokens they hold, and revokes any of
them. A token is shown once, when it is created, so a script or another tool can be given access
without sharing a password. Tokens are django-rest-knox's: it creates them, stores them hashed,
expires them and checks them on each API request. A project without it gets no page, no menu entry
and no import error.

## What this package provides, and what it does not

FS-001 to FS-004 each restyled pages that django-allauth already draws. This feature has no such
page to restyle. django-rest-knox ships API views for signing in and out with a token, and nothing
a person can open in a browser. So for the first time the package provides a page of its own:

- one account management page that lists a person's API tokens, creates one and revokes one;
- its entry and card in the Account Center;
- an optional install extra, so Django REST framework and django-rest-knox arrive at versions the
  package is tested against.

That is all of it. The package adds no model and no migration, and it does not subclass or swap
knox's token model. It generates no token, hashes nothing and checks no request. Creating a token
is a call to knox, and revoking one deletes knox's record. Authenticating an API request is the
job of knox's authentication class, which the host project turns on in its own Django REST
framework settings. The package ships no API endpoint and sets no knox or Django REST framework
setting.

Because the page is built here and not upstream, Article XII asks for the decision to be written
down under `docs/adr/`. FR-014 requires that.

## Clarifications

### Session 2026-10-07

- Q: What turns the feature on, Django REST framework or the token package? → A: The token package.
  The page needs django-rest-knox's records to exist, so it appears when knox is installed and the
  host project has routed the page. A project with Django REST framework and no knox gets nothing,
  the same as a project with neither.
- Q: Does the tokens page need django-allauth? → A: No. It needs a signed-in person and
  django-mvp's Account Center, and nothing from allauth. A project that signs people in some other
  way still gets the page, its entry and its card.
- Q: Can a person name a token, or choose how long it lasts? → A: No to both. knox records no name
  for a token, and adding one would mean replacing its model, which Article XII rules out. How long
  a token lasts is the project's knox setting, the same for everyone. A person tells their tokens
  apart by what knox keeps: the first characters of the token, when it was created and when it
  expires.
- Q: `CONTEXT.md` says a person can see when each token was last used. Is that shown? → A: No.
  knox does not record it. The page shows what knox records, and the glossary entry is corrected in
  the same pull request (FR-013).
- Q: Does revoking ask first? → A: Yes. A revoked token cannot be brought back and whatever was
  using it stops working at once, so the person confirms before it is deleted. FS-004 asks for no
  confirmation only because allauth's page does not, and here there is no upstream page to follow.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer turns on API tokens for a project (Priority: P1)

A developer whose project has a Django REST framework API wants the people using the site to be
able to reach that API from a script. They install this package with its API extra, add
django-rest-knox to the project and run its migrations, include this package's tokens URLs, and
name knox's authentication class in their Django REST framework settings. The Account Center now
has an API tokens entry and card. A developer whose project has no API does none of this, and
their project is unchanged: nothing new appears and nothing fails to import.

**Why this priority**: Nothing else in the feature exists until a project can turn it on, and a
project that has not turned it on must be left alone. Both halves are the adoption promise in G3.

**Independent Test**: In a project with knox installed and the tokens URLs included, open the
Account Center signed in and check the entry and card are there and lead to the tokens page. In a
project without Django REST framework, check the package imports, the Account Center renders, and
it has no tokens entry or card.

**Acceptance Scenarios**:

1. **Given** a project with django-rest-knox installed and the tokens URLs included, **When** a
   signed-in person opens the Account Center, **Then** it has an entry and a card that lead to the
   tokens page.
2. **Given** a project without Django REST framework installed, **When** the project starts and
   the Account Center renders, **Then** nothing raises and there is no tokens entry or card.
3. **Given** a project with Django REST framework installed and django-rest-knox absent, **When**
   the Account Center renders, **Then** there is no tokens entry or card and nothing raises.
4. **Given** a project with django-rest-knox installed that has not included the tokens URLs,
   **When** the Account Center renders, **Then** there is no tokens entry or card.
5. **Given** a project with the tokens page turned on and django-allauth absent, **When** a
   signed-in person opens the Account Center, **Then** the tokens entry and card are there.
6. **Given** the tokens page is turned on, **When** someone who is not signed in requests it,
   **Then** they are sent to sign in and see no tokens.

---

### User Story 2 - A person creates an API token (Priority: P1)

A signed-in person wants a script to reach the site's API as them. They open the tokens page and
create a token. The page shows them the whole token, this one time, and warns them it will not be
shown again. They copy it into their script, and requests the script sends with the token are
answered as that person.

**Why this priority**: Creating a token is the reason the feature exists. It is the only way to
give a script access without handing it a password.

**Independent Test**: In the demo, sign in, open the tokens page, create a token, copy the value
shown, and call the demo's API endpoint with it. The endpoint answers as the signed-in person.
Reload the tokens page and check the token's value is no longer anywhere on it.

**Acceptance Scenarios**:

1. **Given** a signed-in person on the tokens page, **When** they create a token, **Then** the
   response shows the complete token value.
2. **Given** a token has just been created and shown, **When** the person loads the tokens page
   again, **Then** the complete value appears nowhere on it.
3. **Given** a token a person has just created, **When** a request to the project's API carries
   it, **Then** knox authenticates the request as that person.
4. **Given** a project that limits how many tokens a person may hold, and a person already at the
   limit, **When** they try to create another, **Then** no token is created and the page tells
   them the limit has been reached.
5. **Given** a person creates a token, **When** the token is stored, **Then** it is knox's own
   record, with the lifetime the project's knox settings give it.

---

### User Story 3 - A person sees the tokens they hold (Priority: P2)

A signed-in person opens the tokens page to check what has access to the API as them. They see one
row for each token they hold that still works: the first characters of the token, when it was
created and when it expires. With no tokens, the page says so and still offers to create one.

**Why this priority**: A person cannot decide what to revoke until they can see what they hold,
and the list is how they recognise a token after its full value is gone.

**Independent Test**: In the demo, sign in as the seeded person who holds several tokens, open the
tokens page, and check each token has a row with its first characters, creation time and expiry.
Sign in as a person with none and check the page shows an empty state.

**Acceptance Scenarios**:

1. **Given** a person who holds three tokens, **When** they open the tokens page, **Then** it lists
   three rows, each with the first characters of the token, when it was created and when it
   expires.
2. **Given** two people who each hold tokens, **When** one of them opens the tokens page, **Then**
   it lists only their own.
3. **Given** a person with no tokens, **When** they open the tokens page, **Then** it shows an
   empty state and they can still create a token.
4. **Given** a token that never expires, **When** it is listed, **Then** its row marks it as not
   expiring, and does not show an empty or zero date.
5. **Given** a token whose expiry has passed, **When** the tokens page renders, **Then** that token
   is not listed.

---

### User Story 4 - A person revokes a token (Priority: P2)

A person no longer needs a token, or suspects it has leaked. On the tokens page they choose that
token's revoke action and confirm. The token is gone from the list, and the next API request that
carries it is refused. Their other tokens keep working.

**Why this priority**: Being able to cut off one token without touching the others is what makes
it safe to hand tokens out in the first place.

**Independent Test**: In the demo, sign in as the person with several tokens, revoke one, confirm,
and check it has left the list. Call the demo's API endpoint with the revoked token and with one
that was kept: the first is refused and the second is answered.

**Acceptance Scenarios**:

1. **Given** a person who holds three tokens, **When** they revoke one and confirm, **Then** the
   page lists the other two and confirms that the token was revoked.
2. **Given** a token that has been revoked, **When** a request to the project's API carries it,
   **Then** the request is refused.
3. **Given** a person revokes one of their tokens, **When** a request carries one of their other
   tokens, **Then** it is still authenticated.
4. **Given** a person on the confirmation step, **When** they back out, **Then** the token still
   exists and still works.
5. **Given** a signed-in person, **When** they try to revoke a token that belongs to someone else,
   **Then** the token is not deleted and they get the same response as for a token that does not
   exist.
6. **Given** a request to revoke a token that arrives by following a link, with no form
   submission, **When** it is handled, **Then** no token is deleted.

---

### Edge Cases

- knox also creates a token when someone signs in through its own API sign-in view. Those are the
  same records, so they appear in the list and can be revoked like any other.
- A token deleted by other means, such as knox's "sign out everywhere" endpoint or the Django
  admin, no longer appears. Revoking a token that is already gone tells the person it no longer
  exists and raises nothing.
- knox's default lifetime for a token is ten hours, which suits a browser client and not a script
  that runs for months. The page shows whatever expiry the project's setting produces, and the
  README tells the developer which knox setting decides it.
- A project can ask knox to extend a token's expiry each time it is used. The list shows the
  expiry as it stands when the page is loaded.
- A project that has swapped knox's token model for its own gets the same page over the model that
  is active.
- Changing a password does not revoke a person's tokens, because knox does not do so. The README
  says this.
- If the person leaves the page without copying a new token, the value is gone. They revoke that
  token and create another.
- Each press of create makes a new token. Reloading the page that shows a new token does not make
  a second one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package MUST provide one account management page for API tokens, rendered inside
  the host project's application shell and theme in the Account Center, with the shell's
  navigation, like the other account management pages.
- **FR-002**: The page MUST exist only when django-rest-knox is installed and the host project has
  included the package's tokens URLs. The Account Center MUST show an entry and a card for it
  exactly when the page is routed, and neither otherwise.
- **FR-003**: In a project without Django REST framework or without django-rest-knox, the package
  MUST import, its pages MUST render and its menus MUST build. Nothing from either package may be
  imported except in code that runs only when it is installed.
- **FR-004**: Django REST framework and django-rest-knox MUST be offered as an optional install
  extra and MUST NOT be runtime dependencies. Each MUST be bounded to the major versions the
  package's tests run against.
- **FR-005**: The tokens page, its entry and its card MUST NOT depend on django-allauth being
  installed.
- **FR-006**: Only a signed-in person may reach the page, and every list, create and revoke on it
  MUST act on that person's tokens and nobody else's.
- **FR-007**: A person MUST be able to create a token from the page. The token MUST be created by
  django-rest-knox, with the lifetime the project's knox settings give it. The package MUST NOT
  generate, hash or store a token itself.
- **FR-008**: The complete token value MUST be shown to the person once, in the response to
  creating it, with a warning that it cannot be shown again. The package MUST NOT keep the value in
  any lasting form, and no later page may show it.
- **FR-009**: Where the project limits how many tokens a person may hold, the page MUST refuse to
  create one past the limit, counting tokens the way knox does, and MUST tell the person the limit
  has been reached.
- **FR-010**: The page MUST list each of the person's tokens that has not expired, showing the
  first characters of the token, when it was created and when it expires, as knox records them. A
  token with no expiry MUST be marked as not expiring. With no tokens, the page MUST show an empty
  state.
- **FR-011**: A person MUST be able to revoke one chosen token. Revoking MUST ask for confirmation,
  MUST delete knox's record so the token stops authenticating at once, MUST leave every other
  token alone, and MUST confirm to the person that it was done.
- **FR-012**: The package MUST NOT add a model or migration, subclass or replace knox's token
  model, ship an API endpoint, set any knox or Django REST framework setting, or check how either
  is configured.
- **FR-013**: `CONTEXT.md` MUST describe an API token as the page presents it: a person sees the
  first characters of each token, when it was created and when it expires. The claim that they see
  when it was last used MUST be removed.
- **FR-014**: A record under `docs/adr/` MUST state that the package provides the tokens page
  itself because django-rest-knox ships no browser pages, what the page is limited to, and what
  would make that worth revisiting.
- **FR-015**: The README MUST cover how a project turns API tokens on, and that authenticating API
  requests is done by knox's authentication class, which the project sets. It MUST name the knox
  settings that decide a token's lifetime and the limit per person. It MUST say that a token is
  shown once, that tokens carry no name or last-used time, and that changing a password does not
  revoke them. The CHANGELOG MUST record the feature.
- **FR-016**: The demo MUST install Django REST framework and django-rest-knox with the tokens page
  turned on, expose one API endpoint that answers with the person a token belongs to, and seed one
  account with several tokens, so creating, listing and revoking can all be tried and a token can
  be checked against a real request.
- **FR-017**: Every string the package adds MUST be marked for translation.

### Traceability

| Requirement | Story |
|---|---|
| FR-002, FR-003, FR-004, FR-005, FR-012, FR-014 | US1 |
| FR-007, FR-008, FR-009 | US2 |
| FR-010, FR-013 | US3 |
| FR-011 | US4 |
| FR-001, FR-006, FR-015, FR-016, FR-017 | US1, US2, US3, US4 |

### Key Entities

- **API token**: a secret a person creates for themselves to reach the host project's API without
  a browser (`CONTEXT.md`). It is django-rest-knox's record. knox keeps a hash of the token, its
  first characters, the person it belongs to, when it was created and when it expires. The
  complete value exists only at the moment of creation.
- **Tokens page**: the account management page where a signed-in person creates, sees and revokes
  their own API tokens. It is the one page in this package that no upstream package draws.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A signed-in person can go from the Account Center to a working API token without
  leaving the site's pages, and a request carrying that token is answered as them.
- **SC-002**: A token's complete value can be read exactly once. After the response that shows it,
  no page of the site and no record the package writes holds it.
- **SC-003**: A person can see every working token they hold and none that belong to anyone else.
- **SC-004**: After a person revokes a token, the next API request carrying it is refused, and
  their other tokens still work.
- **SC-005**: A project without Django REST framework starts, renders the Account Center and has no
  tokens entry, card or page. A test asserts it.
- **SC-006**: A developer following the README alone can turn API tokens on in a project that
  already has a Django REST framework API.

## Assumptions

- FS-001 is delivered. Its Account Center wiring is what this feature adds an entry and a card to.
  The tokens list is drawn with the table elements FS-004's sessions list uses, so it behaves the
  same way on a narrow screen.
- django-rest-knox is the token package, as the roadmap settles, for the reasons given there: it
  allows several tokens per person, lets them expire, and does not store them in a readable form.
- Installing django-rest-knox, running its migrations, including this package's tokens URLs and
  setting knox's authentication class are the host project's steps. The package checks none of
  them.
- How long a token lasts, how many a person may hold, the token prefix and whether expiry extends
  on use are knox's settings and the project's choices.
- The page does not ask a person to confirm their password or second factor before creating a
  token. That step is django-allauth's, and this page does not depend on allauth.
- Names for tokens and a last-used time are gaps in django-rest-knox. Raising them there is the
  maintainer's decision, and building either here would need its own decision record.
- Tokens issued to third-party applications on a person's behalf are OAuth and out of scope
  (Article XIV). So is anything about what a token is allowed to do: a token acts as the person,
  with whatever the host project permits them.
