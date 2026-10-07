# Prototype — 005 Personal API tokens

A working prototype of the tokens page, built so the maintainer can look at it before anything is
planned (`decisions.md`, D10). The templates, the markup and the words on screen are what is being
proposed. The Python behind them is there to make the screens reachable. It has no tests and is
rebuilt once the screens are settled.

## What exists

**The records the screens read.** django-rest-knox 5.1 keeps one record per token: a hash of the
token, which is also the record's primary key, the first 15 characters of the token, the person it
belongs to, when it was created, and when it expires. The expiry is empty for a token that never
expires. There is no name, no last-used time and no note of what created the token. The complete
value is returned once, by the call that creates the record, and is stored nowhere.

**What is already there to do the job.** knox's manager creates a token with the lifetime the
project set. Deleting the record revokes it. knox's settings hold the limit per person and the word
that goes before the token in the `Authorization` header. knox applies the limit only in its own
sign-in view, so the page has to count for itself. knox has no browser pages.

**The Account Center.** django-mvp draws the area, its sidebar menu and its landing page of cards.
A page joins it by extending `mvp/account/base.html`, which gives it a container as wide as a form
page, and by adding an entry to the area's menu. This package already adds one "Account" group of
entries and one card per page, and each card and entry appears only when its page is routed. The
group itself is added only when django-allauth is installed.

**The components that fit.**

| Need | Component | Where it is already used |
|---|---|---|
| Page heading with one action | `c-mvp.page.title`, `actions` slot | django-mvp's list pages put "Add" there |
| A titled block | `c-mvp.card`, with its `badges` and `footer` slots | the Account Center cards, and every allauth panel in this package |
| The list | `c-table` | the same `table` markup inside a scrolling wrapper as the sessions page |
| Nothing to list | `c-mvp.page.list.empty` | django-mvp's list pages |
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
The seed command prints how the accounts sign in. Running it again puts every state back.

| State | Sign in as | Open |
|---|---|---|
| Entry in the sidebar, and the "API tokens" card | any account | `/account/` |
| Several tokens, one that never expires | `regular.user@example.com` | `/account/tokens/` |
| A token that has expired and is not listed | `regular.user@example.com` | `/account/tokens/`. Four records exist and three are listed |
| No tokens | `staff.user@example.com` | `/account/tokens/` |
| At the limit of five | `super.user@example.com` | `/account/tokens/` |
| A token just created, shown whole | `staff.user@example.com` | `/account/tokens/`, then press **Create token** |
| The same page a moment later, value gone | `staff.user@example.com` | reload, or press **I have copied it** |
| Revoke confirmation | `regular.user@example.com` | `/account/tokens/`, then **Revoke** on any row |
| Revoked, with the message | `regular.user@example.com` | press **Revoke token** on the confirmation |
| Backed out | `regular.user@example.com` | press **Cancel** on the confirmation |
| Someone else's token | any other account | the confirmation address of a token that is not yours answers "not found" |
| A real request | any account | `curl -H "Authorization: Token <value>" <site>/api/whoami/` answers with the account's email, and with 401 once the token is revoked |

## The two questions the specification left open

**How the one-time token is presented.** After **Create token** the person lands back on the
tokens page, and a card titled "Your new token" sits directly under the heading, above the list,
outlined in the warning colour. It holds, in this order: a warning that the token will not be shown
again, the whole token in a read-only field with a **Copy** button joined to it, one line on how to
send it, and a button, **I have copied it**, that leaves the card behind. The field takes focus
when the page loads and selects itself, so Ctrl+C works at once and a screen reader lands on it. In
the list below, the new token's row carries a "New" badge, so the person can see which row the
value belongs to. Nothing else on the page changes, so the card is the only new thing to look at.

**How create, the list and revoke sit together.** Creating has nothing to fill in, so it is one
primary button in the page heading, where django-mvp's list pages put "Add". The list is one card
under it, "Your tokens", with a count against the limit when the project sets one. Each row has its
own **Revoke** button. Revoking opens a confirmation page of its own, which names the token by its
first characters, when it was created and when it expires, says what will stop working, and offers
**Revoke token** and **Cancel**. At the limit the create button is not drawn, and a notice above
the list says why and what to do.

## 1. What the screens need from the code

- The tokens page needs the signed-in person's tokens that have not expired, newest first, each
  with its first characters, when it was created and when it expires.
- A token with no expiry needs to be told apart from one with a date, so its row can read "Never
  expires".
- The count beside "Your tokens" and the notice at the limit need the project's limit per person,
  and need to know when there is none.
- The create button needs to know whether the person is at the limit before the page is drawn.
- The "Your new token" card needs the complete value on the one page view that follows creating
  it, and on no later one.
- The "New" badge needs to know which row was just created, on that same page view only.
- The line on how to send the token needs the word the project's knox settings put before it in
  the `Authorization` header.
- Each row's **Revoke** needs an address that names one token and can be opened with a link.
- The confirmation page needs that one token's first characters, creation time and expiry, and
  needs to answer "not found" for a token that is someone else's, expired or already gone.
- After revoking, the tokens page needs a message that names the token by its first characters.
- The sidebar entry needs to stay marked as current on the confirmation page as well as the list.
- The Account Center needs the entry and the card when the page is routed, and neither otherwise.

## 2. What the prototype faked

- **How the new token reaches the page.** The value is put in the session, the person is
  redirected, and the page takes it out again as it draws. That survives until the next page view,
  which the specification's rule on lasting storage (FR-008, D9) may not allow. The plan decides
  how it travels. What has to hold is what the screen does: the value on one page view, and a
  reload that neither shows it again nor creates a second token.
- **The address of the confirmation page** carries knox's stored hash of the token, because that is
  the record's primary key. A hash in an address ends up in browser history and server logs. The
  plan chooses what names a token in an address.
- **The sidebar entry** is added inside the "Account" group, which is only built when
  django-allauth is installed. The page must not depend on allauth (FR-005, D3), so the entry needs
  a place that exists without it.
- **Turning the page on** is only the demo including the URLs. Nothing checks that
  django-rest-knox is installed, and the package's menu module has not been tried in a project
  without it (FR-002, FR-003).
- **The limit refusal.** A create request sent at the limit is refused with a toast that fades
  after two seconds. The notice above the list is what a person actually reads. Whether a
  refusal needs something that stays on the page is not settled.
- **Revoking a token that is already gone** answers "not found". The specification asks for a
  message saying it no longer exists.
- **Two existing tests fail** because they pin the exact list of menu entries and of this
  package's components, and both lists grew. No test was added or changed.
- **Not built at all:** the decision record (FR-014), the README and CHANGELOG entries (FR-015),
  the `CONTEXT.md` correction (FR-013) and the translation catalogue (FR-017). The strings are
  marked for translation in the templates.
- **The `api` extra's version bounds** (`djangorestframework>=3.15,<4`, `django-rest-knox>=5.0,<6`)
  are a first guess. FR-004 asks for the versions the tests run against.
- **The copy button** falls back to an older browser call on a page served without HTTPS, where
  the clipboard API does not exist. It has not been tried in a browser.

## 3. What was ruled by eye

Nothing has been ruled yet. These are the choices the prototype made where no rule settles the
answer. Each is the maintainer's to change.

| Choice | Intent |
|---|---|
| The new token appears on the tokens page, in a card above the list, and not on a page of its own or in a dialog | The person stays where the token will live, and can see its row appear |
| The card is outlined in the warning colour and carries a warning alert | The one thing that cannot be recovered should be the loudest thing on the page |
| A single-line read-only field with a joined **Copy** button | The token is one value to copy. On a narrow screen the field scrolls and the button still copies all of it |
| **I have copied it** closes the card | Gives the step an end, as the recovery codes page does with its checkbox |
| A "New" badge on the row just created | Ties the value to the row that will remain |
| **Create token** in the page heading, with no confirmation | One primary action for the page, where list pages put theirs. A token made by mistake is one click to revoke |
| The list in a card titled "Your tokens", with "3 of 5" beside the title | The count says how close the limit is before it is reached |
| At the limit the button is removed and a notice explains | A disabled button gives no reason. The notice does |
| Created and expiry as full dates and times, not "3 days ago" | A person recognises a token by when they made it, and knox's default lifetime is hours |
| **Revoke** as a small outlined red button on every row | Visible without a menu, quiet enough to repeat down a column |
| Revoking confirms on its own page, not in a dialog | Works without scripts, has an address to back out from, and matches how the two-factor pages confirm a removal |
| One sentence under the list on what to do about a lost token | The page never shows a value again, so it says what to do instead |
| "API tokens" is the last entry in the "Account" group, with the key icon | It is the newest and the least used of the account pages |

Settled by a rule, and so not open to taste:

- The token's first characters are the row header of each row, and every column header carries its
  scope, so a screen reader names the row by its token.
- Each **Revoke** has an accessible name that includes the token's first characters, because five
  buttons all reading "Revoke" cannot be told apart out of context (WCAG 2.4.6).
- The warning is words and an icon, never colour alone (WCAG 1.4.1).
- Revoking is a form submission. Following a link deletes nothing (specification, US4 scenario 6).
- The table sits in a wrapper that scrolls sideways and can be reached by keyboard, as the
  sessions table does.

## Open questions for the maintainer

1. **The one-time token.** Is a card at the top of the tokens page enough that nobody misses it, or
   should creating a token lead to a page of its own that shows nothing else?
2. **Create, list and revoke on one page.** Is the create button right in the page heading, and is
   a separate confirmation page right for revoking, or should the confirmation be a dialog over the
   list?
