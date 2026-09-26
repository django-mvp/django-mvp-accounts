# Feature Specification: Accounts, sign-in and recovery on the site's own pages

**Feature Branch**: `001-allauth-account-pages`

**Created**: 2026-09-26

**Status**: Draft

**Serves**: G1, a person can sign up, sign in, recover access and manage their account through an
integrated authentication package. G2, every entrance and account page looks like part of the host
project. G3, adopting the package takes as little as possible, and what appears depends on what the
project has installed.

**Roadmap**: R1, accounts, sign-in and recovery

**Issue**: #5

**Input**: A person using a django-mvp site can create an account, sign in and out, get back in after
forgetting their password, and manage their email addresses and password, all on pages that look like
the rest of the site. The package reskins allauth's account app and nothing more. It puts templates
where allauth looks for them, so the pages change as soon as `allauth` and `allauth.account` are in
the project's `INSTALLED_APPS`. It does not configure allauth, depend on it at runtime, or check how a
project has set it up.

## Clarifications

### Session 2026-09-26

- Q: Is allauth a dependency of the package? → A: Only in development, for the demo project and the
  tests. A host project installs and configures allauth itself. The package ships templates that
  allauth picks up, and those templates are never used in a project without allauth.
- Q: Does the package check that a project has set allauth up correctly? → A: No. It adds no system
  checks, no settings defaults and no warnings. A project that has left out allauth's middleware or
  authentication backend gets whatever allauth does about it.
- Q: What does a host project have to do beyond installing allauth? → A: Add this package to
  `INSTALLED_APPS` ahead of `allauth`. Django uses the first matching template it finds among the
  installed apps' template directories, so the order decides whether the reskinned pages or
  allauth's bare ones render. The README says so, and nothing else is required.
- Q: What happens when the host project has already overridden one of allauth's templates? → A: The
  project's own template wins, because Django searches the project's template directories before any
  app's. That is standard Django behaviour and the package does nothing to change it.
- Q: Which pages are in scope? → A: Every page allauth's account app renders, with one exception.
  Sign-up by passkey only exists when allauth's multi-factor app is installed, so it belongs to
  two-factor authentication (#7). The emails allauth sends are out of scope and keep allauth's own
  templates.
- Q: Which allauth versions are supported? → A: The 65.x line, currently 65.19.4. The bound sits in
  the development dependency group, because that is what CI runs. It cannot constrain a host project,
  so the README states the supported range instead.
- Q: Do the strings the package adds need translating? → A: Yes. The menu entries and the account
  overview's text are marked for translation, per Article VIII. Everything else on these pages is
  allauth's text, which allauth already translates.
- Q: Does reskinning a form field change how it is announced to assistive technology? → A: It must
  not. Each field keeps its label, its help text and its errors associated with the input, as
  allauth's own element does.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sign up, sign in and sign out on the site's own pages (Priority: P1)

A visitor to a django-mvp site creates an account, signs in, and later signs out. Each of those pages
carries the site's theme and branding. None of them shows the application shell's navigation,
because someone who is not signed in has nowhere to go yet. When the project has turned on sign-in
by emailed code, the pages for requesting and entering a code look the same way. So do the pages for
sign-up being closed and for an inactive account.

**Why this priority**: Every other account page assumes someone who has signed in, and the sign-in
page is the first page of this package most people will ever see.

**Independent Test**: In the demo project, open the sign-up, sign-in and sign-out pages and the code
sign-in pages. Each response carries the host project's shell and theme without its navigation, and
contains allauth's form for that page.

**Acceptance Scenarios**:

1. **Given** a visitor who is not signed in, **When** they open the sign-in page, **Then** it renders
   inside the site's shell, in the site's theme, without the shell's navigation, and it contains
   allauth's sign-in form.
2. **Given** a visitor on the sign-up page, **When** they submit the form with an error, **Then**
   allauth's error for each field appears next to that field, styled like the site's other form
   errors.
3. **Given** a project with sign-in by emailed code turned on, **When** a visitor requests a code and
   then enters it, **Then** both pages render like the sign-in page.
4. **Given** a project with sign-in by emailed code turned off, **When** a visitor opens the sign-in
   page, **Then** nothing on it offers a code.
5. **Given** a signed-in person, **When** they sign out, **Then** the sign-out page renders like the
   sign-in page, and allauth's "you have signed out" message appears on the page that follows.
6. **Given** a project with sign-up closed, **When** a visitor opens the sign-up page, **Then**
   allauth's "sign-up closed" page renders like the other entrance pages.

---

### User Story 2 - Get back in after forgetting a password (Priority: P1)

A person who has forgotten their password asks for a reset. They follow the link or enter the code
allauth sends, choose a new password, and are told it worked. A person who has just signed up is
asked to verify their email address, by link or by code depending on the project's settings. Every
one of those pages looks like the site's other entrance pages.

**Why this priority**: A site whose members cannot recover their accounts is not usable, and recovery
is half of what this feature is named for.

**Independent Test**: In the demo project, request a password reset, follow the emailed link, set a
new password, and reach the confirmation page. Repeat with code-based reset turned on. Every page
renders as an entrance page.

**Acceptance Scenarios**:

1. **Given** a visitor who has forgotten their password, **When** they request a reset, **Then** the
   request page and the "check your email" page both render as entrance pages.
2. **Given** a valid reset link, **When** the person opens it, sets a new password and submits,
   **Then** the new-password page and the confirmation page both render as entrance pages.
3. **Given** an expired or already-used reset link, **When** the person opens it, **Then** allauth's
   message that the link is invalid renders as an entrance page.
4. **Given** a project with code-based password reset turned on, **When** the person enters the code,
   **Then** the code page renders as an entrance page.
5. **Given** a project that requires email verification, **When** a person signs up, **Then** the
   "verification sent" page, the email confirmation page and the "verified email required" page
   render as entrance pages. With code-based verification turned on, the code page does too.

---

### User Story 3 - Reach account management from anywhere on the site (Priority: P2)

A signed-in person finds "Account" and "Sign out" in the application shell's user menu. "Account"
opens an account overview page listing what they can change about their account. On this feature
alone, that is email addresses and password, plus phone number when the project has turned phone
numbers on. Two-factor authentication, connected social accounts, signed-in sessions and API tokens
will each add to this page later without reorganising it.

**Why this priority**: The individual management pages work without it, since allauth links to them
directly, but people need one obvious place to find them.

**Independent Test**: Sign in to the demo project and open the user menu. It contains "Account" and
"Sign out", and "Account" opens the overview listing the management pages that apply. Then run with
allauth absent, and neither the menu entries nor the overview appear, with no error.

**Acceptance Scenarios**:

1. **Given** a signed-in person, **When** they open the shell's user menu, **Then** it contains
   "Account" and "Sign out".
2. **Given** a visitor who is not signed in, **When** any page renders, **Then** neither entry
   appears.
3. **Given** a signed-in person, **When** they open the account overview, **Then** it renders inside
   the shell with its navigation and lists email addresses and password.
4. **Given** a project with phone numbers turned off, **When** the account overview renders, **Then**
   it does not list a phone number.
5. **Given** a project without allauth installed, **When** any page renders, **Then** no account menu
   entry exists, no account overview is routed, and nothing raises.

---

### User Story 4 - Change email addresses, password and phone number (Priority: P2)

A signed-in person adds an email address, makes one primary, resends a verification, or removes one.
Where the project allows only one address, they change it instead. They change their password, or
set one if they signed up without one. With phone numbers turned on, they change their phone number
and verify it by code. When allauth asks them to confirm who they are before a sensitive change, that
page looks like the rest of account management.

**Why this priority**: It completes what the issue asks for, and allauth already links to these pages,
so they are reachable before the overview exists.

**Independent Test**: Signed in to the demo project, open the email, password and phone pages, make a
change on each, and trigger re-authentication. Every page renders inside the shell with its
navigation and contains allauth's form.

**Acceptance Scenarios**:

1. **Given** a signed-in person with several email addresses, **When** they open the email page,
   **Then** it lists each address with whether it is verified and which one is primary, along with
   allauth's actions for them.
2. **Given** a project that allows only one email address, **When** the person opens the email page,
   **Then** allauth's change-email page renders instead, inside the shell.
3. **Given** a signed-in person with a password, **When** they open the password page, **Then**
   allauth's change-password form renders inside the shell. **Given** one without a password,
   **Then** allauth's set-password form does.
4. **Given** a project with phone numbers turned on, **When** the person changes their phone number
   and enters the code they receive, **Then** both pages render inside the shell.
5. **Given** allauth asks for re-authentication before a change, **When** that page renders, **Then**
   it renders inside the shell like the other account management pages.

---

### Edge Cases

- A host project that already overrides one of allauth's templates keeps its own version.
- A host project that lists this package after `allauth` in `INSTALLED_APPS` gets allauth's bare
  pages. The README says so, and nothing checks for it.
- allauth's shared elements (buttons, fields, alerts, panels) are also used by its social account,
  multi-factor and user sessions apps, so the reskin reaches them wherever they appear. Pages
  specific to those apps are neither reviewed nor tested here. Their own features cover them.
- A message allauth adds, such as "Confirmation email sent", appears in the shell like any other
  Django message.
- A page a later 65.x release adds, which this feature did not cover, still extends allauth's
  layouts and so still renders inside the shell.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every page allauth's account app renders, except sign-up by passkey, MUST render inside
  the host project's application shell and theme once this package, `allauth` and `allauth.account`
  are in `INSTALLED_APPS`.
- **FR-002**: Entrance pages (sign-in, sign-up, sign-out, code sign-in, sign-up closed, account
  inactive, password reset and email verification) MUST render without the shell's navigation.
- **FR-003**: Account management pages (email, change email, password change and set, phone change
  and verification, re-authentication) MUST render with the shell's navigation.
- **FR-004**: allauth's forms, field errors, non-field errors, buttons and alerts MUST render in the
  site's theme, and every error allauth reports MUST be visible on the page.
- **FR-005**: A page MUST show only what allauth itself renders for the project's settings. The
  package MUST NOT add a control, link or page for something the project has turned off.
- **FR-006**: The shell's user menu MUST contain "Account" and "Sign out" for a signed-in person when
  allauth is installed, and neither otherwise.
- **FR-007**: The account overview MUST list the account management pages that apply to the project,
  and MUST let later features add entries to it without changing the existing ones.
- **FR-008**: In a project without allauth installed, the package MUST import and its menus MUST
  build, without any page raising.
- **FR-009**: The package MUST NOT declare allauth as a runtime dependency, set any allauth setting,
  or add system checks about how allauth is configured.
- **FR-010**: The README MUST state everything a project needs to adopt the package: install it and
  allauth, add it to `INSTALLED_APPS` ahead of `allauth`, include allauth's URLs, and the supported
  allauth versions.
- **FR-011**: A host project's own override of an allauth template MUST take precedence over this
  package's.
- **FR-012**: The demo project MUST have allauth installed with every account-app behaviour in scope
  turned on, so every page in this feature can be reached.
- **FR-013**: `CONTEXT.md` MUST describe accounts without saying the authentication package lets a
  person close their account, because allauth does not.
- **FR-014**: Every string the package adds MUST be marked for translation.
- **FR-015**: A reskinned form field MUST keep its label, help text and errors associated with its
  input.

### Traceability

| Requirement | Story |
|---|---|
| FR-001, FR-002, FR-004, FR-005, FR-011, FR-015 | US1, US2 |
| FR-009, FR-010, FR-012, FR-013 | US1 |
| FR-006, FR-007, FR-008, FR-014 | US3 |
| FR-003 | US4 |

### Key Entities

- **Entrance page**: a page someone sees before they are signed in, rendered without the shell's
  navigation (`CONTEXT.md`).
- **Account management page**: a page a signed-in person uses to change their own account, rendered
  with the shell's navigation (`CONTEXT.md`).
- **Account overview**: the account management page "Account" opens, listing the others.
- **allauth layout**: the base template allauth's pages extend. There is one for entrance pages and
  one for management pages, and overriding them is how every page picks up the shell.
- **allauth element**: one of allauth's small templates for a single piece of markup, such as a
  button or a form field. Overriding them is how allauth's forms pick up the theme.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every account-app page in scope renders inside the shell in the demo project, and a
  test for each page fails if that page falls back to allauth's bare markup.
- **SC-002**: A project adopts the package in two steps beyond setting up allauth: install it, and
  list it ahead of `allauth` in `INSTALLED_APPS`.
- **SC-003**: With allauth absent, the package imports, menus build and pages render, with zero
  account menu entries and zero errors.
- **SC-004**: For each behaviour a project can turn off (code sign-in, code reset, code verification,
  phone numbers, sign-up), a test confirms nothing on any page offers it when it is off.
- **SC-005**: Every error allauth attaches to a form in the demo appears on the rendered page.

## Assumptions

- allauth's account app keeps rendering its pages through its layout and element templates across the
  65.x line, which is what this feature relies on.
- django-mvp's shell provides the user menu and the message display used here. A gap in either is
  raised on django-mvp, not worked around.
- The emails allauth sends keep allauth's own templates.
- django-accounts-center is read only for which pages it had to cover, never for how it built them.
