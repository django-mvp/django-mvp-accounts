# Feature Specification: Sign in with social accounts

**Feature Branch**: `002-social-account-pages`

**Created**: 2026-09-26

**Status**: Draft

**Serves**: G1, a person can sign up, sign in and manage their account through an integrated
authentication package. G2, every entrance and account page looks like part of the host project.
G3, what appears depends on what the project has installed and configured.

**Roadmap**: R2, connected social accounts

**Issue**: #6

**Depends on**: #5, which reskins the account app's pages, form elements and the Account Center
entries this feature adds to.

**Input**: A person signs up and signs in with an account they already have elsewhere, such as
GitHub or Google, and connects or disconnects those accounts from their account management pages.
The package reskins allauth's social account app the same way it reskins the account app: templates
where allauth looks for them, no configuration, no checks, and no runtime dependency on allauth.
Every "sign in with" button carries an icon named after the provider, and the host project supplies
that icon.

## Clarifications

### Session 2026-09-26

- Q: Which providers get a button? → A: Exactly the ones allauth lists for the project's
  configuration. The package draws allauth's own list and never builds one from settings.
- Q: How does a provider button get its logo? → A: Each button renders a `<c-icon>` whose name is
  allauth's provider id, such as `github` or `google`. The provider's display name stays as the
  button's text. The host project makes sure its django-easy-icons setup has an icon under that
  name. The package ships no provider icons.
- Q: What happens when the host project has not mapped an icon for a configured provider? → A:
  Whatever django-easy-icons does. It raises an error unless the project sets
  `EASY_ICONS_FAIL_SILENTLY`, in which case the button shows its text alone. The README states the
  requirement and that behaviour. The package does not check for missing icons.
- Q: Where does the connected-accounts page appear in account management? → A: As an entry and a
  card in the Account Center, added the same way FS-001 adds the email and password pages. It
  appears whenever allauth's connections page is routed, even before any provider is configured,
  because allauth's page works with none.
- Q: How can every page be reached in the demo without real provider credentials? → A: The demo
  installs allauth's test provider (`allauth.socialaccount.providers.dummy`), which runs the whole
  sign-in flow locally, and maps an icon under its provider id.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sign in or sign up with an external account (Priority: P1)

A visitor sees a button for each provider the project has configured on the sign-in and sign-up
pages, each with the provider's name and icon. They choose one, confirm on allauth's "continue"
page, and come back signed in. When the external account lacks something the site needs, such as
an email address, allauth asks for it on an extra sign-up step. If they cancel at the provider, or
the provider fails, they see allauth's page saying so. Every one of these pages is an entrance page.

**Why this priority**: Signing in with an existing account is what the feature is for. Managing
connections only matters once people can sign in this way.

**Independent Test**: In the demo, open the sign-in page, choose the test provider, continue, and
finish signed in. Repeat through the extra sign-up step, a cancelled sign-in and a failed one. Each
page renders as an entrance page, and the sign-in and sign-up pages carry one button per configured
provider, each with an icon named after the provider id.

**Acceptance Scenarios**:

1. **Given** a project with two providers configured, **When** a visitor opens the sign-in page,
   **Then** it shows exactly two provider buttons, each with the provider's name as text and a
   `<c-icon>` named after the provider id.
2. **Given** a project with no providers configured, **When** a visitor opens the sign-in page,
   **Then** it shows no provider buttons and nothing empty in their place.
3. **Given** a visitor who chose a provider, **When** allauth asks them to confirm, **Then** the
   confirmation page renders as an entrance page with allauth's "continue" button.
4. **Given** an external account without an email address the site requires, **When** the visitor
   returns from the provider, **Then** allauth's extra sign-up step renders as an entrance page with
   its form and any errors visible.
5. **Given** a visitor who cancels at the provider, or a provider that returns an error, **When**
   they come back, **Then** allauth's cancelled or error page renders as an entrance page.

---

### User Story 2 - Connect and disconnect external accounts (Priority: P2)

A signed-in person opens "Connected accounts" from the Account Center. They see the external
accounts connected to theirs and can disconnect any of them. The same provider buttons, with the
same icons, let them connect another. If disconnecting would leave them with no way to sign in,
allauth refuses and says why, and that message is visible on the page.

**Why this priority**: People need to manage the connections they create, but only after they can
sign in with them.

**Independent Test**: Signed in to the demo, open the Account Center, follow "Connected accounts",
connect the test provider, then disconnect it. The page renders as an account management page
throughout, and removing the only way to sign in shows allauth's refusal.

**Acceptance Scenarios**:

1. **Given** a signed-in person, **When** they open the Account Center, **Then** it has a
   "Connected accounts" entry and card.
2. **Given** a project without the social account app installed, **When** the Account Center
   renders, **Then** it has no "Connected accounts" entry or card, and nothing raises.
3. **Given** a person with one connected account, **When** they open the connected-accounts page,
   **Then** it renders as an account management page, lists that account with allauth's disconnect
   action, and shows the provider buttons for connecting another.
4. **Given** a person with no connected accounts, **When** they open the page, **Then** allauth's
   "no connected accounts" message renders and the provider buttons are still shown.
5. **Given** a person whose only way to sign in is one connected account, **When** they try to
   disconnect it, **Then** allauth's refusal appears on the page.

---

### Edge Cases

- A provider configured in the project but without an icon in its django-easy-icons setup raises
  unless the project sets `EASY_ICONS_FAIL_SILENTLY`. That is django-easy-icons' behaviour and the
  package does not intercept it.
- allauth lists each OpenID brand as its own button, all under the provider id `openid`. Every
  such button gets the `openid` icon, because allauth gives the button no other id.
- A host project that already overrides one of allauth's social account templates keeps its own.
- Messages allauth adds after connecting or disconnecting an account appear in the shell like any
  other Django message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every page allauth's social account app renders MUST render inside the host project's
  application shell and theme once this package and `allauth.socialaccount` are installed.
- **FR-002**: The confirmation, extra sign-up step, cancelled and error pages MUST render as
  entrance pages, without the shell's navigation.
- **FR-003**: The connected-accounts page MUST render as an account management page, with the
  shell's navigation.
- **FR-004**: The sign-in and sign-up pages MUST show one button per provider allauth lists for the
  project, and none when it lists none.
- **FR-005**: Every provider button MUST render a `<c-icon>` whose name is allauth's provider id,
  with the provider's display name as its visible text.
- **FR-006**: The package MUST NOT ship provider icons, map icon names, or check that a provider's
  icon exists.
- **FR-007**: The Account Center MUST show a "Connected accounts" entry and card when allauth's
  connections page is routed, and neither otherwise.
- **FR-008**: Every error and message allauth reports on these pages, including its refusal to
  disconnect a person's only way to sign in, MUST be visible on the rendered page.
- **FR-009**: The package MUST NOT declare the social account app as a runtime dependency, set any
  of its settings, or configure providers.
- **FR-010**: The README MUST state that a project enabling social sign-in needs an icon under each
  configured provider's id, and what happens when one is missing.
- **FR-011**: The demo MUST install allauth's test provider and map an icon for it, so every page in
  this feature can be reached without external credentials.
- **FR-012**: Every string the package adds MUST be marked for translation.

### Traceability

| Requirement | Story |
|---|---|
| FR-001, FR-002, FR-004, FR-005, FR-006, FR-009, FR-010, FR-011 | US1 |
| FR-003, FR-007 | US2 |
| FR-008, FR-012 | US1, US2 |

### Key Entities

- **Provider**: allauth's term for an external sign-in service, such as GitHub or Google. It has an
  id (`github`) and a display name ("GitHub").
- **Social account**: an external account connected to a person's account on the host project.
- **Provider icon**: the icon the host project's django-easy-icons setup renders under a provider's
  id.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every social account page renders inside the shell in the demo, and a test for each
  page fails if that page falls back to allauth's bare markup.
- **SC-002**: The number of provider buttons on the sign-in page equals the number of providers
  allauth lists, including zero.
- **SC-003**: Every provider button's icon name equals its provider id, in every test that renders a
  button.
- **SC-004**: With the social account app absent, the Account Center has no "Connected accounts"
  entry or card and no page raises.
- **SC-005**: A person can complete sign-in, connection and disconnection with the demo's test
  provider without leaving the site's pages.

## Assumptions

- FS-001 is delivered first. Its reskinned form elements and Account Center wiring are what this
  feature adds to.
- allauth's social account app keeps drawing its provider buttons through its `provider` element
  across the 65.x line.
- django-mvp's `<c-icon>` keeps passing its name to django-easy-icons.
- Provider configuration and provider icons belong to the host project.
