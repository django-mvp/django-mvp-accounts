# Decisions — 005 Personal API tokens

The issue was specified without a round of questions to the maintainer. Each place where the issue
and the roadmap were silent is listed here with the reading chosen. The maintainer then reviewed a
working prototype on 2026-10-08, and D4 and D11 to D13 record what that review decided.

## The reading the specification is built on

A person signed in to a site with a Django REST framework API opens an API tokens page in the
Account Center, creates a token with a lifetime they choose and sees it once, sees the tokens they
hold, and revokes any one of them. django-rest-knox does everything to do with the token itself.
This package provides the pages, because knox has none, the Account Center entry and card, a
setting for who may hold tokens, and an optional install extra. A project that has not installed
knox and routed the pages gets nothing. The work serves G4, G2 and G3, and it is the whole of
roadmap item R5. No other issue cites R5.

## D1 — The package provides the tokens pages itself

FS-001 to FS-004 restyled pages allauth draws. django-rest-knox 5.1 ships three API views (sign
in, sign out, sign out everywhere), an admin registration and no templates, so there is nothing to
restyle. R5's first deliverable is a page, so the package builds one.

Article XII says a feature upstream lacks is raised there first and building it here is recorded
under `docs/adr/`. Browser pages for account management are outside what knox sets out to do, so
no upstream issue is proposed, and the spec requires the decision record (FR-014). The pages are
kept to three actions over knox's own records: list, create, revoke.

**ADR:** required, written in the build (FR-014).

## D2 — knox being installed turns it on, and the project routes the pages

The issue says a project without Django REST framework gets nothing. The pages cannot work without
knox's records either, so the test is knox, which cannot be installed without Django REST
framework. The package has no URLs of its own today. A page needs one, so the project includes the
package's tokens URLs, and the entry and card appear when that URL resolves. That is the rule ADR
0002 already uses for allauth's pages.

**ADR:** none, ADR 0002's rule applied to one more page.

## D3 — The page does not need allauth

`CONTEXT.md` says the package is not tied to one authentication package. The tokens page needs a
signed-in person and the Account Center and nothing from allauth, so it is not hidden when allauth
is absent. Today the Account Center group this package adds is built only when allauth is
installed, so the build has to place the tokens entry without relying on that.

**ADR:** none, covered by the decision record D1 requires.

## D4 — No token names and no last-used time, and a lifetime the person chooses

knox's token record holds a hash, the first characters of the token, the owner, a creation time
and an expiry. It has no name and no last-used time.

Names are not provided in the specification as it stands. Storing one needs somewhere to put it.
Swapping knox's model is ruled out by Article XII ("never subclasses one of their models"), and
the package adds no model of its own (FR-012). The maintainer wants a way to name a token, so a
person knows what each was made for, and has said that how to do it is a question for planning and
review and not one to settle in a prototype. It is recorded in `planning-notes.md`, which the plan
must answer by name.

A last-used time stays out. Recording it would mean writing on every API request, which is knox's
job, and the package checks no request.

A lifetime chosen by the person is in: see D11.

`CONTEXT.md` currently says a person can "see when each was last used". That was written before
the backend was read closely, and the spec corrects it (FR-013).

**ADR:** none, nothing is built. Recorded as upstream gaps in the spec's assumptions.

## D5 — Revoking asks for confirmation

FS-004 signs out other sessions with no confirmation, because allauth's page has none. Here there
is no upstream page to follow. A revoked token cannot be restored and whatever uses it breaks at
once, so the person confirms first.

**ADR:** none, local to one action.

## D6 — Expired tokens are not listed

knox removes an expired token the next time it is presented, or the next time that person signs in
through knox, so expired records can linger. They cannot be used, and listing them next to working
tokens would make the list harder to trust. The list shows tokens that have not expired, which is
also how knox counts tokens against the per-person limit.

**ADR:** none.

## D7 — The page honours knox's per-person limit

knox enforces `TOKEN_LIMIT_PER_USER` in its sign-in view and not in the call that creates a token.
A page that ignored it would let a person past a limit the project set, so the page applies the
same count before creating (FR-009).

**ADR:** none, covered by the decision record D1 requires.

## D8 — No re-authentication before creating a token

A token is worth as much as a password, and allauth can ask a person to confirm who they are before
a sensitive change. Using that here would tie the tokens page to allauth, against D3. A token made
from a hijacked session lasts as long as whoever made it chose, which can be for good, and shows up
in the list, where it can be revoked. Left out, and named as an open risk on the pull request.

**ADR:** none.

## D9 — "Shown once" is a storage rule as well as a display rule

The spec says the package keeps the complete value in no lasting form (FR-008). How the value gets
from the create action to the one response that shows it is for planning, with that rule as the
constraint: nothing that survives that response may hold it.

**ADR:** none.

## D10 — The feature gets a prototype before it is planned

This is the first page in the package whose layout is the package's own. Every earlier page took
its structure from allauth. Two things had no precedent to copy: how the one-time token is
presented so a person does not miss it, and how creating, the list and revoking sit together.
Those are judgements for the maintainer's eye, and a test cannot settle them. The feature
therefore stops for a prototype review before any planning.

The review settled both. The one-time token is shown on the tokens page, in a card above the
list. Revoking confirms on a page of its own. `sketch.md` records the screens as reviewed.

**ADR:** none.

## D11 — A person chooses a lifetime from a short fixed list

The maintainer's review asked how a person sets when a token expires, and there was no way.
Creating a token is now a small form on a page of its own that asks for its lifetime: 7 days, 30
days, 90 days, 1 year, or never. 30 days is selected to begin with, so a person who does not think
about it gets a token that expires. The list is fixed in the package. Making it a setting is left
until a project asks, under Article II.

The choice is passed to knox as the token's expiry, which needs nothing stored by this package.
knox's `TOKEN_TTL` setting is therefore not used for these tokens. It still decides the lifetime of
tokens knox's own views create. The limit per person is unchanged and still knox's setting (D7).

A list and not a date field, because a person choosing a lifetime is choosing roughly how long,
and a list cannot produce a date in the past. Offering "never" is deliberate: a long-running
script is the case the feature exists for, and the alternative is a person re-issuing tokens by
hand or choosing the longest option without thinking.

**ADR:** none, local to one form.

## D12 — The list shows days without a time

The list shows the first characters of each token, the day it was created and the day it expires.
The time of day is left out: it made the table cramped, and the shortest lifetime on offer is a
week.

**ADR:** none.

## D13 — One setting says who may hold tokens

Some sites give API access to a few people, such as staff, and everyone else must see nothing of
it. The project points one setting at a function that takes a person and returns whether they may
hold tokens. With no setting, every signed-in person may. The setting is read in one place, and
that one answer decides the Account Center entry, the card and every tokens page. There is no
registry and no settings object, under Articles II and III.

Article XIV puts permissions out of scope, and this does not cross it. The package still decides
nothing about what a signed-in person may do, and nothing about what a token may do. It asks the
project one question, who gets these pages, and the project's own function answers it. The package
ships no rule of its own beyond "everyone".

The check covers the pages only. It does not revoke tokens a person already holds and it is not
consulted when a token is used, because the package checks no API request. A project that needs
that deletes the tokens or checks in its own API.

**ADR:** none, covered by the decision record D1 requires.

## D14 — The new token travels in a signed cookie, not the session

FR-008 says the package keeps the complete value in no lasting form. The prototype used the
session, which Django writes to a database table by default. The build sets a signed, HTTP-only
cookie on the redirect after creating, scoped to the tokens page and good for a minute, and the
tokens page deletes it as it shows the value. The server stores nothing, and a reload finds
nothing. Rendering the token in the response to the form submission was the other candidate, and
a reload would then create a second token. `research.md` R3 has the comparison.

**ADR:** none, local to one redirect. Covered by the decision record D1 requires.

## D15 — A token is named in an address by knox's `token_key`

The confirmation page needs an address for one token. knox's primary key is its stored hash,
which does not belong in browser history or server logs. `token_key`, the token's first
characters, is what the list already shows and what knox itself looks tokens up by. Every lookup
starts from the signed-in person's own working tokens.

**ADR:** none, local to one route.

## D16 — One response for a token that is gone, expired or someone else's

The confirmation page answers all three the same way: nothing is deleted, and the person is sent
back to the tokens page with a message that the token no longer exists. The spec asks for a
message when a token is already gone and for a stranger's token to be indistinguishable from a
missing one. One response does both.

**ADR:** none.

## D17 — The setting is `MVP_ACCOUNTS_API_TOKEN_ACCESS`, and a bad path raises

The name is the package, the thing and what it decides. The path is resolved with Django's
`import_string` each time it is asked, and a path that does not import raises `ImportError` naming
it. No system check is added, in line with FR-012.

**ADR:** none.

## D18 — Token names are answered in research and left for the maintainer

`planning-notes.md` asks for a way to name a token. `research.md` compares the ways. The only one
that works on every project without replacing knox's model is a model of this package's own, which
FR-012 and the maintainer's ruling keep out of this build. The feature is built without names, and
the recommendation goes to the maintainer at review: a follow-up feature on a one-to-one model,
with the gap raised upstream.

**ADR:** none, nothing is built.
