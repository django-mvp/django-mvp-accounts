# Feature Specification: Organisations

**Feature Branch**: `006-organisations`

**Created**: 2026-11-09

**Status**: Draft

**Serves**: G6, a person can belong to organisations: create one, invite others to it, see and
manage its members and their roles, and switch between the organisations they are in. G2, the
organisation pages look like part of the host project. G3, the pages, their menu entry and their
card appear only in a project that has installed django-organizations and routed the pages.

**Roadmap**: R7, organisations

**Issue**: #70

**Depends on**: #5, delivered, which put the account management pages in django-mvp's Account
Center. The organisation pages are added to them.

**Input**: A person belongs to organisations as well as having their own account: a family sharing
one plan, a teacher's class, a language school, a research group. From their account pages they
create an organisation, invite people to it by email, and see who its members are. Its owner and
admins change a member's role or remove them, and anyone can leave. Someone who belongs to more
than one organisation switches between them and can always see which one they are working in.
Organisations come from django-organizations, so a project that has not installed it gets nothing
from this. What membership lets a person do with the project's own objects stays the project's to
decide.

## What this package provides, and what it does not

django-organizations keeps organisations, their members, each member's role and invitations. It
ships pages for listing, creating, renaming and deleting organisations, for the members list, for
adding, editing and removing a member, and for reminding someone of an invitation. This package
draws those pages inside django-mvp's application shell and Account Center, as it does allauth's.

django-organizations has no way for a member to leave an organisation, no page for handing over
ownership, and no idea of the organisation a person is working in. Its own invitation flow signs a
new person up with a form of its own. This package provides those four parts itself:

- leaving an organisation;
- handing ownership to another member;
- the current organisation, and switching between organisations;
- joining after signing up through the site's own sign-up pages.

The package adds no organisation model and no migration of its own, and subclasses none of
django-organizations' models ([ADR 0007](../../docs/adr/0007-organisations-come-from-django-organizations.md)).
A role says who runs an organisation and nothing more. What a member may do with the host
project's objects is the host project's to decide. Paying for an organisation's places belongs to
django-mvp-payments.

## Clarifications

### Session 2026-11-09

- Q: What roles does an organisation have? → A: django-organizations' own. Each organisation has one
  owner. Every other member is an admin or a member. The owner is also an admin. There are no other
  roles.
- Q: Who may create an organisation? → A: By default, every signed-in person. One setting names a
  function that takes a person and says whether they may, the same way API tokens are limited
  (FS-005). A person who may not still sees the organisations they belong to.
- Q: Who may invite people, rename the organisation and manage members? → A: Its owner and admins,
  as django-organizations decides. Deleting the organisation and handing over ownership are the
  owner's alone. Every member may see the members list and leave.
- Q: How does someone without an account join? → A: The invitation sends them to the site's own
  sign-up, the one allauth draws, with its email verification and social sign-in. Once signed up
  they arrive back at the invitation and accept it. django-organizations' own registration form is
  never shown.
- Q: Who may accept an invitation? → A: A signed-in person whose account holds the email address the
  invitation was sent to. Anyone else who opens the link is told it was meant for another address,
  and nothing changes. See `decisions.md`, D4.
- Q: Which organisation is a person working in when they first sign in? → A: Their first
  organisation, by name. A switch lasts for that browser session and is not saved to the account.
  A person who belongs to no organisation is working in none.
- Q: Can the owner leave? → A: Not while they own it. They hand ownership to another member first,
  or delete the organisation.
- Q: How does a developer use the current organisation? → A: Their own views ask the package which
  organisation the signed-in person is working in, and get that organisation or none. What they do
  with it is theirs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer turns on organisations and uses them in their own views (Priority: P1)

A developer whose project groups people wants them to be able to form organisations. They install
this package with its organisations extra, add django-organizations to the project and run its
migrations, and include this package's organisation URLs. The Account Center now has an
Organisations entry and card. In their own views they can ask which organisation the signed-in
person is working in. If they want to keep creating organisations to some people, they name one
function in a setting. A developer who does none of this has a project that is unchanged.

**Why this priority**: Nothing else in the feature exists until a project can turn it on, and a
project that has not must be left alone. The current organisation is what any later use of
organisations in the project, payments included, is built on.

**Independent Test**: In a project with django-organizations installed and the URLs included, open
the Account Center signed in and check the entry and card lead to the organisations page, and that
a view in the demo reports the organisation the person is working in. In a project without
django-organizations, check the package imports, the Account Center renders, and nothing about
organisations appears.

**Acceptance Scenarios**:

1. **Given** a project with django-organizations installed and the organisation URLs included,
   **When** a signed-in person opens the Account Center, **Then** it has an entry and a card that
   lead to the organisations page.
2. **Given** a project without django-organizations installed, **When** the project starts and the
   Account Center renders, **Then** nothing raises and there is no organisations entry, card or
   switcher.
3. **Given** a project with django-organizations installed that has not included the organisation
   URLs, **When** the Account Center renders, **Then** there is no organisations entry, card or
   switcher.
4. **Given** organisations are turned on and django-allauth is absent, **When** a signed-in person
   opens the Account Center, **Then** the organisations entry and card are there.
5. **Given** a signed-in person working in an organisation, **When** a view of the host project
   asks for their current organisation, **Then** it gets that organisation. **Given** a person who
   belongs to none, or who is not signed in, **Then** it gets none.
6. **Given** a project whose setting says a person may not create organisations, **When** that
   person opens the organisations page or submits the create form, **Then** they are not offered
   creating one and the form refuses them, and the organisations they already belong to are still
   listed.
7. **Given** organisations are turned on, **When** someone who is not signed in requests an
   organisation page, **Then** they are sent to sign in.

---

### User Story 2 - A person creates an organisation and invites people to it (Priority: P1)

A signed-in person wants to bring their family, their class or their research group together. From
the Account Center they create an organisation and give it a name, and become its owner. They
invite people by email address. Each invited person gets an email with a link. Until someone
accepts, the owner and admins see the invitation as pending and can send a reminder. Later the
owner or an admin can rename the organisation, and the owner can delete it.

**Why this priority**: An organisation has to exist and have a way to gain members before anything
else in the feature means anything.

**Independent Test**: In the demo, sign in, create an organisation, invite an address and check the
email arrives with a working link, the invitation is listed as pending, and a reminder sends the
email again. Rename the organisation, then delete it, and check it is gone from the person's list.

**Acceptance Scenarios**:

1. **Given** a signed-in person who may create organisations, **When** they create one with a name,
   **Then** it exists, they are its owner, and it appears in their list of organisations.
2. **Given** an owner or admin, **When** they invite an email address, **Then** an invitation email
   is sent to it, drawn on the site's branded email layout, and the invitation is listed as pending.
3. **Given** a pending invitation, **When** an owner or admin sends a reminder, **Then** the email is
   sent again and the invitation is unchanged.
4. **Given** an owner or admin, **When** they invite an address that already belongs to a member,
   **Then** no invitation is sent and they are told that person is already a member.
5. **Given** a member who is not an admin, **When** they try to invite someone, rename the
   organisation or send a reminder, **Then** they are not offered it and the request is refused.
6. **Given** an owner or admin, **When** they rename the organisation, **Then** every member sees
   the new name.
7. **Given** the owner, **When** they confirm deleting the organisation, **Then** it is gone, its
   members belong to it no longer, and its pending invitations no longer work. An admin is not
   offered deleting it.

---

### User Story 3 - A person joins an organisation they were invited to, and can leave it (Priority: P1)

A person gets an invitation by email and opens the link. If they are signed in with an account that
has that address, they accept and are a member. If they have no account, they sign up on the
site's own sign-up pages and come back to the invitation to accept it. Any member can later leave
an organisation.

**Why this priority**: Inviting someone is only worth anything if they can get in, including people
who have never used the site.

**Independent Test**: In the demo, open an invitation link signed in as the invited person and
accept it. Open another as nobody, sign up with the invited address and check the invitation is
waiting to be accepted afterwards. Then leave the organisation and check it is gone from the
person's list.

**Acceptance Scenarios**:

1. **Given** a signed-in person whose account holds the invited address, **When** they open the
   invitation and accept it, **Then** they are a member of the organisation with the member role,
   and the invitation is no longer pending.
2. **Given** someone not signed in and with no account, **When** they open the invitation, **Then**
   they are offered the site's own sign-up, and once signed up they are back at the invitation to
   accept it.
3. **Given** someone not signed in who has an account, **When** they open the invitation, **Then**
   they are offered signing in, and once signed in they are back at the invitation.
4. **Given** a signed-in person whose account does not hold the invited address, **When** they open
   the invitation, **Then** they are told it was sent to another address and they do not join.
5. **Given** an invitation that has been accepted, or whose organisation was deleted, **When** its
   link is opened again, **Then** nobody joins and the person is told it can no longer be used.
6. **Given** a person who is invited, **When** they decline or ignore the invitation, **Then** they
   do not join.
7. **Given** a member who is not the owner, **When** they confirm leaving the organisation, **Then**
   they are no longer a member and it is gone from their list.
8. **Given** the owner, **When** they look for a way to leave, **Then** they are told to hand
   ownership to another member or delete the organisation first, and they are still the owner.

---

### User Story 4 - The owner or an admin manages the members (Priority: P2)

Every member can see who belongs to the organisation and what role each has. The owner and admins
can make a member an admin, make an admin a member again, or remove someone. The owner can hand
ownership to another member, for example before leaving.

**Why this priority**: An organisation can run on its owner alone, but it cannot be kept tidy or
handed on without this.

**Independent Test**: In the demo, sign in as an organisation's owner, make a member an admin, make
them a member again, remove another member, and hand ownership to an admin. Check each change shows
on the members list, and that a plain member sees the list with no way to change it.

**Acceptance Scenarios**:

1. **Given** a member, **When** they open the members list, **Then** they see every member and each
   one's role, and the owner marked as owner.
2. **Given** an owner or admin, **When** they make a member an admin, or an admin a member, **Then**
   that person's role changes and nobody else's does.
3. **Given** an owner or admin, **When** they confirm removing a member, **Then** that person
   belongs to the organisation no longer.
4. **Given** an owner or admin, **When** they look for a way to remove the owner or change the
   owner's role, **Then** they are not offered it and the request is refused.
5. **Given** the owner, **When** they confirm handing ownership to another member, **Then** that
   member is the owner, and the former owner stays on as an admin.
6. **Given** an admin who is not the owner, **When** they try to hand over ownership, **Then** they
   are not offered it and the request is refused.
7. **Given** a person who is not a member, **When** they request any page of an organisation,
   **Then** they are refused and learn nothing about it.

---

### User Story 5 - A person switches between their organisations (Priority: P2)

A teacher who is also in a family organisation wants to work in one at a time. Wherever they are on
the site they can see which organisation they are working in, and switch to another of theirs.

**Why this priority**: Most people belong to one organisation, and for them the first one is always
the current one. Switching matters once someone belongs to more than one.

**Independent Test**: In the demo, sign in as a person in two organisations, check the current one
is shown, switch to the other, and check the shown organisation and the demo's report of the
current organisation both change and stay changed across pages.

**Acceptance Scenarios**:

1. **Given** a signed-in person who belongs to organisations, **When** they open any page in the
   application shell, **Then** they can see which organisation they are working in.
2. **Given** a person who belongs to more than one organisation, **When** they switch to another
   one of theirs, **Then** it is their current organisation on every page until they switch again or
   sign out.
3. **Given** a person who has just signed in, **When** nothing has been switched yet, **Then** their
   current organisation is their first by name.
4. **Given** a person who belongs to no organisation, **When** they open a page, **Then** nothing
   about a current organisation is shown and nothing raises.
5. **Given** a person whose current organisation they leave, are removed from, or is deleted,
   **When** they next load a page, **Then** their current organisation is their first remaining one
   by name, or none.
6. **Given** a person, **When** they try to switch to an organisation they do not belong to,
   **Then** nothing changes.

---

### Edge Cases

- Someone invited by two organisations gets two invitations, and accepting one leaves the other
  pending.
- An invitation to an address that later joins the site through social sign-in is accepted the same
  way, once the account holds that address.
- A person removed from an organisation can be invited again.
- Deleting a person's account removes them from every organisation, as django-organizations
  arranges. What happens to an organisation whose owner's account is deleted is
  django-organizations' answer, and the README says so.
- Organisation names need not be unique.
- An organisation with only its owner is a normal organisation.
- A project that turns organisations off after people have formed them keeps django-organizations'
  records. The package simply stops drawing anything about them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package MUST draw django-organizations' pages for organisations and their members
  inside the host project's application shell and theme, in the Account Center, like the other
  account management pages: the list of a person's organisations, creating, renaming and deleting
  an organisation, the members list, inviting a person, changing a member's role, removing a member
  and reminding an invitee.
- **FR-002**: The pages MUST exist only when django-organizations is installed and the host project
  has included the package's organisation URLs. The Account Center MUST show an entry and a card for
  them exactly when the organisations page is routed, and neither otherwise.
- **FR-003**: In a project without django-organizations, the package MUST import, its pages MUST
  render and its menus MUST build. Nothing from django-organizations may be imported except in code
  that runs only when it is installed.
- **FR-004**: django-organizations MUST be offered as an optional install extra, bounded to the
  major versions the package's tests run against, and MUST NOT be a runtime dependency.
- **FR-005**: The organisation pages, their entry, their card and the current organisation MUST NOT
  depend on django-allauth being installed, except joining after sign-up (FR-011), which uses
  allauth's sign-up where it is installed.
- **FR-006**: Only a signed-in person may reach the pages. Every page of an organisation MUST refuse
  a person who is not its member. Who may invite, rename, remind, change roles and remove members
  MUST be django-organizations' answer: the owner and admins. Deleting the organisation and handing
  over ownership MUST be the owner's alone.
- **FR-007**: A host project MUST be able to say who may create organisations, through one setting
  that names a function taking a person and returning whether they may. Without the setting, every
  signed-in person may. A person who may not MUST NOT be offered creating one, and the create page
  MUST refuse them, whether loaded or submitted to.
- **FR-008**: Creating an organisation MUST make the person who created it its owner.
- **FR-009**: Inviting MUST use django-organizations' model-tracked invitations. The invitation and
  reminder emails MUST be drawn on django-mvp's branded email layout. Inviting an address that
  already belongs to a member MUST send nothing and say so.
- **FR-010**: An invitation MUST be accepted only by a signed-in person whose account holds the
  address it was sent to. Accepting MUST make them a member with the member role. An accepted
  invitation, or one whose organisation is gone, MUST NOT let anyone join.
- **FR-011**: Someone who opens an invitation without being signed in MUST be offered the site's own
  sign-in and sign-up, and MUST return to the invitation once signed in. django-organizations' own
  registration form MUST NOT be reachable.
- **FR-012**: A member who is not the owner MUST be able to leave an organisation after confirming.
  The owner MUST NOT be able to leave while they own it.
- **FR-013**: The owner MUST be able to hand ownership to another member after confirming. The new
  owner MUST be made an admin if they were not one, and the former owner MUST remain an admin.
  It MUST NOT be possible to remove the owner or change the owner's role.
- **FR-014**: Every page in the application shell MUST let a signed-in person who belongs to
  organisations see which one they are working in and switch to another of theirs. The switch MUST
  last for that browser session. Before any switch, and whenever the current one is no longer
  theirs, the current organisation MUST be their first remaining by name, or none.
- **FR-015**: The package MUST offer the host project's views one way to get the organisation the
  signed-in person is working in, returning that organisation or none.
- **FR-016**: The package MUST NOT add a model or migration, subclass or replace django-organizations'
  models, give a role any meaning in the host project, or set any django-organizations setting
  except the invitation backend it requires, which the README MUST name.
- **FR-017**: `CONTEXT.md` MUST define organisation, member, owner, admin, invitation and current
  organisation.
- **FR-018**: A record under `docs/adr/` MUST name each part the package builds that
  django-organizations does not have (leaving, handing over ownership, the current organisation and
  switching, and joining after the site's own sign-up), why each is built here, and what would make
  it worth revisiting.
- **FR-019**: The README MUST cover how a project turns organisations on, the setting for who may
  create them, how a view gets the current organisation, that a role grants nothing in the host
  project, and that paying for places is django-mvp-payments'. The CHANGELOG MUST record the
  feature.
- **FR-020**: The demo MUST install django-organizations with the pages turned on, and seed an
  organisation with an owner, an admin, a member and a pending invitation, a person who belongs to
  two organisations, and a person who belongs to none, so every page and every state can be tried.
  It MUST have one page that reports the current organisation.
- **FR-021**: Every string the package adds MUST be marked for translation.

### Traceability

| Requirement | Story |
|---|---|
| FR-002, FR-003, FR-004, FR-005, FR-007, FR-015, FR-016, FR-018 | US1 |
| FR-008, FR-009 | US2 |
| FR-010, FR-011, FR-012 | US3 |
| FR-013 | US4 |
| FR-014 | US5 |
| FR-001, FR-006, FR-017, FR-019, FR-020, FR-021 | US1, US2, US3, US4, US5 |

### Key Entities

- **Organisation**: a group of accounts with a name, kept by django-organizations. It has one
  owner and any number of other members.
- **Member**: a person who belongs to an organisation, with the role owner, admin or member. The
  owner is also an admin. A role says who runs the organisation and grants nothing in the host
  project.
- **Invitation**: django-organizations' record of an email address invited to an organisation, by
  whom, and whether it has been accepted.
- **Current organisation**: the one of a person's organisations they are working in during a
  browser session. Kept for the session only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A signed-in person can create an organisation, invite someone, and see that person
  listed as a member once they accept, without leaving the site's pages.
- **SC-002**: Someone with no account can go from an invitation email to being a member, through
  the site's own sign-up, without being shown django-organizations' registration form.
- **SC-003**: Nobody who is not a member of an organisation can see its name, its members or its
  invitations. A test asserts each page.
- **SC-004**: Every change to a member's role, every removal and every handover is allowed for
  exactly the people FR-006 names and refused for everyone else. A test asserts each.
- **SC-005**: A person in two organisations can switch between them, and the current organisation a
  host view receives matches the one shown, on every page.
- **SC-006**: A project without django-organizations starts, renders the Account Center and shows
  nothing about organisations. A test asserts it.
- **SC-007**: A developer following the README alone can turn organisations on and read the current
  organisation in a view of their own.

## Assumptions

- FS-001 is delivered. Its Account Center wiring is what this feature adds an entry and a card to,
  and its sign-in and sign-up pages are where an invitee without an account goes.
- django-organizations 2.7 is the organisations package, as ADR 0007 settles. It runs on Django 6.1
  and brings django-extensions with it.
- Installing django-organizations, running its migrations and including this package's URLs are
  the host project's steps.
- Withdrawing a pending invitation and making invitations expire are not in django-organizations
  and not in this specification.
- Paying for an organisation's places, and codes that give someone a place, are django-mvp-payments
  R4. What membership lets a person do with the host project's objects is the host project's,
  with whatever permissions package it uses (Article XIV).
- An organisation's public profile, or settings beyond its name, are not account management and
  are out of scope (ADR 0007, "Revisit if").
