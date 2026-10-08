# Feature Specification: Personal API tokens

**Feature Branch**: `005-personal-api-tokens`

**Created**: 2026-10-07

**Status**: Draft

**Serves**: G4, when the project has a REST API a person can create, see and revoke their own API
tokens. G2, the tokens pages look like part of the host project. G3, the pages, their menu entry
and their card appear only in a project that has installed the token package and routed the pages,
and only for the people the project lets hold tokens.

**Roadmap**: R5, personal API tokens

**Issue**: #35

**Depends on**: #5, delivered, which put the account management pages in django-mvp's Account
Center. The tokens page is one more of them.

**Input**: When a project has a REST API built on Django REST framework, a person creates API
tokens for reaching it from their account pages, chooses when each expires, sees which tokens they
hold, and revokes any of them. A token is shown once, when it is created, so
a script or another tool can be given access without sharing a password. Tokens are
django-rest-knox's: it creates them, stores them hashed, expires them and checks them on each API
request. A project that has not turned the feature on gets no page, no menu entry and no import
error, and a project that has can say which people may hold tokens.

## What this package provides, and what it does not

FS-001 to FS-004 each restyled pages that django-allauth already draws. This feature has no such
page to restyle. django-rest-knox ships API views for signing in and out with a token, and nothing
a person can open in a browser. So for the first time the package provides pages of its own:

- account management pages that list a person's API tokens, create one and revoke one;
- the entry and card for those pages in the Account Center;
- one setting that lets the project say which people may hold tokens;
- an optional install extra, so Django REST framework and django-rest-knox arrive at versions the
  package is tested against.

That is all of it. The package adds no model and no migration, and it does not subclass or swap
knox's token model. It generates no token, hashes nothing and checks no request. Creating a token
is a call to knox, with the lifetime the person chose, and revoking one deletes knox's record.
Authenticating an API request is the job of knox's authentication class, which the host project
turns on in its own Django REST framework settings. The package ships no API endpoint and sets no
knox or Django REST framework setting.

Because the pages are built here and not upstream, Article XII asks for the decision to be written
down under `docs/adr/`. FR-014 requires that.

## Clarifications

### Session 2026-10-07

- Q: What turns the feature on, Django REST framework or the token package? → A: The token package.
  The pages need django-rest-knox's records to exist, so they appear when knox is installed and the
  host project has routed them. A project with Django REST framework and no knox gets nothing,
  the same as a project with neither.
- Q: Does the tokens page need django-allauth? → A: No. It needs a signed-in person and
  django-mvp's Account Center, and nothing from allauth. A project that signs people in some other
  way still gets the pages, their entry and their card.
- Q: Can a person name a token? → A: Not in this specification. knox records no name for a token,
  and the package adds no model of its own to hold one (FR-012). A person tells their tokens apart
  by what knox keeps: the first characters of the token, the day it was created and the day it
  expires. The maintainer wants a way to name tokens, and how to provide one is an open question
  for planning and review, recorded in `planning-notes.md`.
- Q: Can a person choose how long a token lasts? → A: Yes. Creating a token asks for a lifetime
  from a short list that includes one that never expires. The project's knox `TOKEN_TTL` setting
  then decides the lifetime only of tokens knox's own views create.
- Q: `CONTEXT.md` says a person can see when each token was last used. Is that shown? → A: No.
  knox does not record it. The page shows what knox records, and the glossary entry is corrected in
  the same pull request (FR-013).
- Q: Does revoking ask first? → A: Yes. A revoked token cannot be brought back and whatever was
  using it stops working at once, so the person confirms before it is deleted. FS-004 asks for no
  confirmation only because allauth's page does not, and here there is no upstream page to follow.
- Q: Can a project keep API tokens to some of its people? → A: Yes. One setting names a function
  that takes a person and says whether they may hold tokens. Without it, every signed-in person
  may. A person who may not sees no entry and no card, and the pages refuse them.

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
5. **Given** a project with the tokens pages turned on and django-allauth absent, **When** a
   signed-in person opens the Account Center, **Then** the tokens entry and card are there.
6. **Given** the tokens pages are turned on, **When** someone who is not signed in requests one,
   **Then** they are sent to sign in and see no tokens.

---

### User Story 2 - A person creates an API token (Priority: P1)

A signed-in person wants a script to reach the site's API as them. They open the tokens page and
choose to create a token. A short form asks when the token should expire. They pick a lifetime and
create it. The tokens page then shows them the whole token, this one
time, and warns them it will not be shown again. They copy it into their script, and requests the
script sends with the token are answered as that person.

**Why this priority**: Creating a token is the reason the feature exists. It is the only way to
give a script access without handing it a password.

**Independent Test**: In the demo, sign in as a person who may hold tokens, open the tokens page,
create a token with a chosen lifetime, copy the value shown, and call the demo's API endpoint
with it. The endpoint answers as the signed-in person. Reload the tokens page and check the token's
value is no longer anywhere on it, and that its row shows the expiry that was chosen.

**Acceptance Scenarios**:

1. **Given** a signed-in person on the create page, **When** they choose a lifetime and create the
   token, **Then** they land on the tokens page and it shows the complete token
   value.
2. **Given** a token has just been created and shown, **When** the person loads the tokens page
   again, **Then** the complete value appears nowhere on it.
3. **Given** a token a person has just created, **When** a request to the project's API carries
   it, **Then** knox authenticates the request as that person.
4. **Given** a project that limits how many tokens a person may hold, and a person already at the
   limit, **When** they try to create another, **Then** no token is created and the page tells
   them the limit has been reached.
5. **Given** a person creates a token with a chosen lifetime, **When** the token is stored,
   **Then** it is knox's own record and it expires when the chosen lifetime says.
6. **Given** a person chooses a token that never expires, **When** it is created, **Then** knox's
   record has no expiry.
7. **Given** a person on the create page, **When** they back out, **Then** no token is created.

---

### User Story 3 - A person sees the tokens they hold (Priority: P2)

A signed-in person opens the tokens page to check what has access to the API as them. They see one
row for each token they hold that still works: the first characters of the token, the day it was
created and the day it expires. With no tokens, the page says so and still offers to create one.

**Why this priority**: A person cannot decide what to revoke until they can see what they hold,
and the list is how they recognise a token after its full value is gone.

**Independent Test**: In the demo, sign in as the seeded person who holds several tokens, open the
tokens page, and check each token has a row with its first characters, the day it was created and
the day it expires. Revoke them all and check the page shows an empty state.

**Acceptance Scenarios**:

1. **Given** a person who holds three tokens, **When** they open the tokens page, **Then** it lists
   three rows, each with the first characters of the token, the day it was created and the day it
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

### User Story 5 - A developer limits who may hold API tokens (Priority: P2)

A developer runs a site where only some people should reach the API, such as its staff. They point
one setting at a function of their own that takes a person and says whether that person may hold
API tokens. People the function lets in see the tokens entry and card and use the pages as before.
Everyone else sees no sign of the feature in their Account Center, and is refused if they go to a
tokens address directly. A developer who sets nothing changes nothing: every signed-in person may
hold tokens.

**Why this priority**: On a site where tokens are for a few people, showing the pages to everyone
offers something most of them must not have. The developer needs one place to say who.

**Independent Test**: In the demo, where the setting lets in staff only, sign in as the person who
is not staff and check the Account Center has no tokens entry or card and that the tokens
addresses refuse them. Sign in as a staff person and check the entry, the card and the pages are
there.

**Acceptance Scenarios**:

1. **Given** a project that has not set who may hold tokens, **When** any signed-in person opens
   the Account Center, **Then** the tokens entry and card are there and the pages serve them.
2. **Given** a project whose setting lets in staff only, **When** a staff person opens the Account
   Center, **Then** the tokens entry and card are there and the pages serve them.
3. **Given** the same project, **When** a person who is not staff opens the Account Center,
   **Then** there is no tokens entry and no tokens card.
4. **Given** the same project, **When** a person who is not staff requests the tokens page, the
   create page or a revoke page, by loading it or by submitting to it, **Then** the request is
   refused, no token is created or deleted, and no token is shown.
5. **Given** the same project, **When** someone who is not signed in requests a tokens page,
   **Then** they are sent to sign in, as in any other project.

---

### Edge Cases

- knox also creates a token when someone signs in through its own API sign-in view. Those are the
  same records, so they appear in the list and can be revoked like any other.
- A token deleted by other means, such as knox's "sign out everywhere" endpoint or the Django
  admin, no longer appears. Revoking a token that is already gone tells the person it no longer
  exists and raises nothing.
- A token made on the tokens page lasts as long as the person chose. The project's knox `TOKEN_TTL`
  setting decides the lifetime only of tokens knox's own views create, and its default of ten hours
  suits a browser client. The README says which is which.
- Limiting who may hold tokens does not revoke tokens a person already holds. Someone who held
  tokens and is later shut out keeps working tokens until they expire or the project deletes them,
  because the package checks no API request. The README says so.
- A project can ask knox to extend a token's expiry each time it is used. The list shows the
  expiry as it stands when the page is loaded.
- A project that has swapped knox's token model for its own gets the same page over the model that
  is active.
- Changing a password does not revoke a person's tokens, because knox does not do so. The README
  says this.
- If the person leaves the page without copying a new token, the value is gone. They revoke that
  token and create another.
- Each submission of the create form makes a new token. Reloading the page that shows a new token
  does not make a second one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package MUST provide account management pages for API tokens, rendered inside
  the host project's application shell and theme in the Account Center, with the shell's
  navigation, like the other account management pages: one that lists a person's tokens, one that
  creates a token, and one that confirms revoking a token.
- **FR-002**: The pages MUST exist only when django-rest-knox is installed and the host project has
  included the package's tokens URLs. The Account Center MUST show an entry and a
  card for them exactly when the tokens page is routed and the person may hold tokens (FR-019), and
  neither otherwise.
- **FR-003**: In a project without Django REST framework or without django-rest-knox, the package
  MUST import, its pages MUST render and its menus MUST build. Nothing from either package may be
  imported except in code that runs only when it is installed.
- **FR-004**: Django REST framework and django-rest-knox MUST be offered as an optional install
  extra and MUST NOT be runtime dependencies. Each MUST be bounded to the major versions the
  package's tests run against.
- **FR-005**: The tokens pages, their entry and their card MUST NOT depend on django-allauth being
  installed.
- **FR-006**: Only a signed-in person may reach the pages, and every list, create and revoke on
  them MUST act on that person's tokens and nobody else's.
- **FR-007**: A person MUST be able to create a token from the pages. The token MUST be created by
  django-rest-knox, with the lifetime the person chose (FR-018). The package MUST NOT generate,
  hash or store a token itself.
- **FR-008**: The complete token value MUST be shown to the person once, on the tokens page they
  reach after creating it, with a warning that it cannot be shown again. The package MUST NOT keep
  the value in any lasting form, and no later page may show it.
- **FR-009**: Where the project limits how many tokens a person may hold, the pages MUST refuse to
  create one past the limit, counting tokens the way knox does, and MUST tell the person the limit
  has been reached.
- **FR-010**: The tokens page MUST list each of the person's tokens that has not expired, showing
  the first characters of the token, the day it was created and the day it expires, as knox records
  them. A token with no expiry MUST be marked as not expiring. With no tokens, the page MUST show
  an empty state.
- **FR-011**: A person MUST be able to revoke one chosen token. Revoking MUST ask for confirmation,
  MUST delete knox's record so the token stops authenticating at once, MUST leave every other
  token alone, and MUST confirm to the person that it was done.
- **FR-012**: The package MUST NOT add a model or migration, subclass or replace knox's token
  model, ship an API endpoint, set any knox or Django REST framework setting, or check how either
  is configured.
- **FR-013**: `CONTEXT.md` MUST describe an API token as the pages present it: a person chooses
  when each token expires, and sees its first characters, the day it was created and the day it
  expires.
  The claim that they see when it was last used MUST be removed.
- **FR-014**: A record under `docs/adr/` MUST state that the package provides the tokens pages
  itself because django-rest-knox ships no browser pages, what the pages are limited to, and what
  would make that worth revisiting.
- **FR-015**: The README MUST cover how a project turns API tokens on, and that authenticating API
  requests is done by knox's authentication class, which the project sets. It MUST cover the
  setting that says who may hold tokens, and that it does not revoke tokens already held. It MUST
  name the knox setting for the limit per person, and say that knox's lifetime setting reaches only
  tokens knox's own views create. It MUST say that a token is shown once, that tokens carry no
  name or last-used time, and that changing a password does not revoke them. The CHANGELOG MUST
  record the feature.
- **FR-016**: The demo MUST install Django REST framework and django-rest-knox with the tokens
  pages turned on and limited to staff, expose one API endpoint that answers with the person a
  token belongs to, and seed one staff account with several tokens, one account at the limit
  and one account that may not hold tokens, so creating, listing, revoking and being shut out can
  all be tried and a token can be checked against a real request.
- **FR-017**: Every string the package adds MUST be marked for translation.
- **FR-018**: Creating a token MUST ask the person to choose its lifetime from a short fixed list
  that includes a token that never expires, with one choice already selected. The choice MUST be
  passed to django-rest-knox as the token's expiry.
- **FR-019**: A host project MUST be able to say which people may hold API tokens, through one
  setting that names a function taking a person and returning whether they may. Without the
  setting, every signed-in person may. The same answer MUST decide the Account Center entry, the
  card and every tokens page: a person who may not hold tokens sees no entry and no card, and
  every tokens page refuses them, whether loaded or submitted to.

### Traceability

| Requirement | Story |
|---|---|
| FR-002, FR-003, FR-004, FR-005, FR-012, FR-014 | US1 |
| FR-007, FR-008, FR-009, FR-018 | US2 |
| FR-010, FR-013 | US3 |
| FR-011 | US4 |
| FR-019 | US5 |
| FR-001, FR-006, FR-015, FR-016, FR-017 | US1, US2, US3, US4, US5 |

### Key Entities

- **API token**: a secret a person creates for themselves to reach the host project's API without
  a browser (`CONTEXT.md`). It is django-rest-knox's record. knox keeps a hash of the token, its
  first characters, the person it belongs to, when it was created and when it expires. The
  complete value exists only at the moment of creation.
- **Tokens pages**: the account management pages where a signed-in person creates, sees and
  revokes their own API tokens. They are the only pages in this package that no upstream package
  draws.

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
- **SC-007**: On a site that limits tokens to some people, a person outside that group finds no
  entry, no card and no page that serves them. A test asserts each.

## Assumptions

- FS-001 is delivered. Its Account Center wiring is what this feature adds an entry and a card to.
  The tokens list is drawn with the same table markup as FS-004's sessions list, so it behaves the
  same way on a narrow screen.
- django-rest-knox is the token package, as the roadmap settles, for the reasons given there: it
  allows several tokens per person, lets them expire, and does not store them in a readable form.
- Installing django-rest-knox, running its migrations, including this package's tokens URLs and
  setting knox's authentication class are the host project's steps. The package checks none of
  them.
- How many tokens a person may hold, the token prefix and whether expiry extends on use are knox's
  settings and the project's choices. The lifetimes a person can choose from are the package's and
  are the same for every project.
- The function that says who may hold tokens is the project's. The package calls it and decides
  nothing about what a token is allowed to do.
- The pages do not ask a person to confirm their password or second factor before creating a
  token. That step is django-allauth's, and these pages do not depend on allauth.
- Names for tokens and a last-used time are gaps in django-rest-knox. Raising them there is the
  maintainer's decision. How a person might name a token is an open question for planning and
  review (`planning-notes.md`), and building it here would need its own decision record.
- Tokens issued to third-party applications on a person's behalf are OAuth and out of scope
  (Article XIV). So is anything about what a token is allowed to do: a token acts as the person,
  with whatever the host project permits them.
