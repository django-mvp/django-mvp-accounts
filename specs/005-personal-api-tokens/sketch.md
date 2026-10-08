# Prototype — 005 Personal API tokens

A working prototype of the tokens pages, built so the maintainer can look at them before anything
is planned (`decisions.md`, D10). The templates, the markup and the words on screen are what is
being proposed. The Python behind them is there to make the screens reachable. It has no tests and
is rebuilt once the screens are settled.

## What exists

**The records the screens read.** django-rest-knox 5.1 keeps one record per token: a hash of the
token, which is also the record's primary key, the first 15 characters of the token, the person it
belongs to, when it was created, and when it expires. The expiry is empty for a token that never
expires. There is no name, no last-used time and no note of what created the token. The complete
value is returned once, by the call that creates the record, and is stored nowhere.

**What is already there to do the job.** knox's manager creates a token and takes the lifetime as
an argument. Deleting the record revokes it. knox's settings hold the limit per person and the word
that goes before the token in the `Authorization` header. knox applies the limit only in its own
sign-in view, so the pages have to count for themselves. knox has no browser pages and nowhere to
keep a name for a token.

**The Account Center.** django-mvp draws the area, its sidebar menu and its landing page of cards.
A page joins it by extending `mvp/account/base.html`, which gives it a container as wide as a form
page, and by adding an entry to the area's menu. An entry can carry a check that hides it from some
requests. This package already adds one "Account" group of entries and one card per page, and each
card and entry appears only when its page is routed. Until now the group was built only when
django-allauth is installed.

**The components that fit.**

| Need | Component | Where it is already used |
|---|---|---|
| Page heading with one action | `c-mvp.page.title`, `actions` slot, `inline_actions` | django-mvp's list pages put "Add" there |
| A titled block | `c-mvp.card`, with its `badges` and `footer` slots | the Account Center cards, and every allauth panel in this package |
| The list | `c-table` | the same `table` markup inside a scrolling wrapper as the sessions page |
| Nothing to list | `c-mvp.page.list.empty` | django-mvp's list pages |
| A form drawn from a Django form | `c-mvp.form` with `form-obj` | django-mvp's create and update pages |
| A warning that stays on the page | `c-alert` | the allauth pages |
| A read-only value with a button joined to it | `c-form.input` inside `c-join` | new here. The recovery codes page shows its codes in a read-only field, without a button |
| A label over a value | `c-mvp.data_field` | django-mvp's detail pages |
| "It was done" | Django messages, drawn by the shell as a toast | every allauth page |

**Where a component is missing.** Nothing in django-mvp or daisy-cotton copies a value to the
clipboard as a component. django-mvp does it inline in two places (its share menu and its
documentation block). The prototype adds one component of this package's own,
`c-mvp_accounts.token.created`, which holds the read-only field, the copy button and the warning.

## The screens, and how to reach each state

Run `uv run python manage.py migrate` and `uv run python manage.py seed_demo`, then start the demo.
The seed command prints how the accounts sign in. Running it again puts every state back. The demo
lets only staff hold tokens.

| State | Sign in as | Open |
|---|---|---|
| Entry in the sidebar, and the "API tokens" card, last | `staff.user@example.com` | `/account/` |
| No entry and no card | `regular.user@example.com` | `/account/` |
| Refused | `regular.user@example.com` | `/account/tokens/` and `/account/tokens/create/` |
| Several tokens, one that never expires | `staff.user@example.com` | `/account/tokens/` |
| A token that has expired and is not listed | `staff.user@example.com` | `/account/tokens/`. Four records exist and three are listed |
| At the limit of five | `super.user@example.com` | `/account/tokens/` |
| The create form | `staff.user@example.com` | `/account/tokens/create/`, or **Create token** on the tokens page |
| A token just created, shown whole | `staff.user@example.com` | choose a lifetime on the create form and submit |
| The same page a moment later, value gone | `staff.user@example.com` | reload, or press **I have copied it** |
| Revoke confirmation | `staff.user@example.com` | `/account/tokens/`, then **Revoke** on any row |
| Revoked, with the message | `staff.user@example.com` | press **Revoke token** on the confirmation |
| Backed out | `staff.user@example.com` | press **Cancel** on the confirmation or on the create form |
| No tokens | `staff.user@example.com` | revoke all three. Seeding again brings them back |
| Someone else's token | `super.user@example.com` | the confirmation address of a staff token answers "not found" |
| A real request | `staff.user@example.com` | `curl -H "Authorization: Token <value>" <site>/api/whoami/` answers with the account's email, and with 401 once the token is revoked |

## The pages

**The tokens page.** A heading with one **Create token** button beside it, and under it a card,
"Your tokens", with a count against the limit when the project sets one. Each row is the first
characters of a token, the day it was created, the day it expires and its own **Revoke** button.
At the limit the create button is not drawn, and a notice above the list says why
and what to do.

**The create page.** A page of its own, the same shape as the revoke confirmation: one card with a
choice of lifetime, 30 days already selected, a line saying the token is shown
once on the next page, and **Create token** and **Cancel**.

**A token just created.** Back on the tokens page, a card titled "Your new token" sits directly
under the heading, above the list, outlined in the warning colour. It holds a warning
that the token will not be shown again, the whole token in a read-only field with a **Copy** button
joined to it, one line on how to send it, and **I have copied it**. The field takes focus when the
page loads and selects itself. The new token's row carries a "New" badge.

**The revoke confirmation.** A page of its own that names the token by its first characters, shows
when it was created and when it expires, says what will stop working, and offers **Revoke token** and **Cancel**.

## 1. What the screens need from the code

- The tokens page needs the signed-in person's tokens that have not expired, newest first, each
  with its first characters, the day it was created and the day it expires.
- A token with no expiry needs to be told apart from one with a date, so its row can read "Never".
- The count beside "Your tokens" and the notice at the limit need the project's limit per person,
  and need to know when there is none.
- The create button and the create page need to know whether the person is at the limit.
- The create form needs a lifetime from a fixed list with one choice selected.
- Creating needs the chosen lifetime to become the token's expiry.
- The new-token card needs the complete value on the one page view that follows creating it, and
  on no later one.
- The "New" badge needs to know which row was just created, on that same page view only.
- The line on how to send the token needs the word the project's knox settings put before it in
  the `Authorization` header.
- Each row's **Revoke** needs an address that names one token and can be opened with a link.
- The confirmation page needs that one token's first characters, creation day and expiry, and needs to answer
  "not found" for a token that is someone else's, expired or already gone.
- After revoking, the tokens page needs a message that names the token by its first characters.
- The sidebar entry needs to stay marked as current on the create and confirmation pages.
- The entry, the card and every tokens page need one answer to "may this person hold tokens",
  taken from the project.
- The Account Center needs the entry and the card when the page is routed and the person may hold
  tokens, and neither otherwise.

## 2. What the prototype faked

- **How the new token reaches the page.** The value is put in the session, the person is
  redirected, and the page takes it out again as it draws. That survives until the next page view,
  which the specification's rule on lasting storage (FR-008, D9) may not allow. The plan decides
  how it travels. What has to hold is what the screen does: the value on one page view, and a
  reload that neither shows it again nor creates a second token.
- **The address of the confirmation page** carries knox's stored hash of the token, because that is
  the record's primary key. A hash in an address ends up in browser history and server logs. The
  plan chooses what names a token in an address.
- **Turning the pages on** is only the demo including the URLs. Nothing checks that
  django-rest-knox is installed, and the package's menu and template tag have not been tried in a
  project without it (FR-002, FR-003).
- **The refusal for a person who may not hold tokens** is Django's bare "403 Forbidden" page in
  the demo, which sets no error handlers. Whether refused means "forbidden" or "not found" is not
  settled either.
- **The limit refusal.** Opening the create page at the limit sends the person back to the list
  with a toast that fades after two seconds. The notice above the list is what a person reads.
- **Revoking a token that is already gone** answers "not found". The specification asks for a
  message saying it no longer exists.
- **The setting's name**, `MVP_ACCOUNTS_API_TOKEN_ACCESS`, is a first guess, and a path that does
  not import raises on the first page that asks.
- **Three existing tests fail** because they pin the exact list of Account Center entries, with
  and without django-allauth, and of this package's components, and those lists grew. No test was
  added or changed.
- **Not built at all:** the decision record (FR-014), the README and CHANGELOG entries (FR-015),
  the `CONTEXT.md` correction (FR-013) and the translation catalogue (FR-017). The strings are
  marked for translation.
- **The `api` extra's version bounds** (`djangorestframework>=3.15,<4`, `django-rest-knox>=5.0,<6`)
  are a first guess. FR-004 asks for the versions the tests run against.
- **The copy button** falls back to an older browser call on a page served without HTTPS, where
  the clipboard API does not exist. It has not been tried in a browser.
- **The create button staying on one line** was checked in the markup, not in a browser: the
  button's text cannot wrap and its container cannot shrink.

No longer faked: the sidebar entry does not depend on django-allauth. It joins the "Account" group
when there is one and brings the group when there is not.

## 3. What was ruled by eye

Ruled by the maintainer on 2026-10-08. The build may not undo these.

| Ruling | Outcome |
|---|---|
| The one-time token | Shown on the tokens page, in a card above the list. It is clear enough there |
| Confirming a revoke | On a page of its own, not in a dialog |
| The **Create token** button | Its text stays on one line at every width |
| A person sets the expiry | Creating is a form on a page of its own, with a choice of lifetime |
| The list shows part of the token | Columns are the token's first characters, created and expires |
| No model and no app of the package's own | The prototype stores nothing. Naming tokens is left to planning and review (`planning-notes.md`) |
| Dates without a time of day | For created and expires, in the list and on the confirmation |
| Who may hold tokens | The project can limit it. A person outside sees no entry and no card, and the pages refuse them |

Choices the prototype made where no rule settles the answer. Each is the maintainer's to change.

| Choice | Intent |
|---|---|
| Lifetimes of 7 days, 30 days, 90 days, 1 year and never, with 30 days selected | Short enough by default that a forgotten token goes away, with a long option and "never" for a script that runs unattended |
| The lifetime is a drop-down list labelled "Expires after" | Five choices in the space of one field. The page stays as short as the revoke page |
| A token that never expires reads "Never" in the Expires column | The column heading already says "Expires" |
| The card is outlined in the warning colour and carries a warning alert | The one thing that cannot be recovered should be the loudest thing on the page |
| A single-line read-only field with a joined **Copy** button | The token is one value to copy. On a narrow screen the field scrolls and the button still copies all of it |
| **I have copied it** closes the card | Gives the step an end, as the recovery codes page does with its checkbox |
| A "New" badge on the row just created | Ties the value to the row that will remain |
| The list in a card titled "Your tokens", with "3 of 5" beside the title | The count says how close the limit is before it is reached |
| At the limit the button is removed and a notice explains | A disabled button gives no reason. The notice does |
| **Revoke** as a small outlined red button on every row | Visible without a menu, quiet enough to repeat down a column |
| One sentence under the list on what to do about a lost token | The page never shows a value again, so it says what to do instead |
| "API tokens" is the last entry in the "Account" group and the last card | It is the newest and the least used of the account pages |

Settled by a rule, and so not open to taste:

- The token's first characters are the row header of each row, and every column header carries
  its scope, so a screen reader names the row by its token.
- Each **Revoke** has an accessible name that includes the token's first characters, because
  several buttons all reading "Revoke" cannot be told apart out of context (WCAG 2.4.6).
- The lifetime field has a visible label and is marked as required (WCAG 3.3.2).
- The warning is words and an icon, never colour alone (WCAG 1.4.1).
- Revoking and creating are form submissions. Following a link changes nothing (specification, US4
  scenario 6).
- The table sits in a wrapper that scrolls sideways and can be reached by keyboard, as the
  sessions table does.

## Open questions for the maintainer

1. **The lifetimes.** Are 7 days, 30 days, 90 days, 1 year and never the right list, and is 30 days
   the right one to start on?
2. **Being refused.** Should a person who may not hold tokens be told "forbidden" at a tokens
   address, as now, or "not found", so the pages give no sign they exist?
