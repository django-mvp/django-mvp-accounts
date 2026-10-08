# Decisions — 005 Personal API tokens

The issue was specified without a round of questions to the maintainer. Each place where the issue
and the roadmap were silent is listed here with the reading chosen. The maintainer then reviewed a
working prototype on 2026-10-08, and D4 and D11 to D14 record what that review decided.

## The reading the specification is built on

A person signed in to a site with a Django REST framework API opens an API tokens page in the
Account Center, creates a token with a name and a lifetime and sees it once, sees the tokens they
hold by name, and revokes any one of them. django-rest-knox does everything to do with the token
itself. This package provides the pages, because knox has none, the name, because knox records
none, the Account Center entry and card, a setting for who may hold tokens, and an optional install
extra. A project that has not added the tokens app and routed the pages gets nothing. The work
serves G4, G2 and G3, and it is the whole of roadmap item R5. No other issue cites R5.

## D1 — The package provides the tokens pages itself

FS-001 to FS-004 restyled pages allauth draws. django-rest-knox 5.1 ships three API views (sign
in, sign out, sign out everywhere), an admin registration and no templates, so there is nothing to
restyle. R5's first deliverable is a page, so the package builds one.

Article XII says a feature upstream lacks is raised there first and building it here is recorded
under `docs/adr/`. Browser pages for account management are outside what knox sets out to do, so
no upstream issue is proposed, and the spec requires the decision record (FR-014). The pages are
kept to three actions over knox's own records: list, create, revoke. The same record covers the
model in D11.

**ADR:** required, written in the build (FR-014).

## D2 — Adding the tokens app turns it on, and the project routes the pages

The feature lives in an app of its own, `mvp_accounts.tokens`, which a project adds to
`INSTALLED_APPS`. It has to be an app because it has a model (D11), and a model needs an app a
project can choose to install. That makes the on-switch something the developer does on purpose,
and it keeps every import of knox and Django REST framework inside code that is only loaded when
the app is installed, which is what Article XIII asks for. A project that installs knox for some
other reason and does not add the app gets nothing.

The project also includes the app's URLs, and the entry and card appear when the tokens page
resolves. That is the rule ADR 0002 already uses for allauth's pages.

**ADR:** none, ADR 0002's rule applied to one more page. The app itself is covered by the decision
record D1 requires.

## D3 — The page does not need allauth

`CONTEXT.md` says the package is not tied to one authentication package. The tokens page needs a
signed-in person and the Account Center and nothing from allauth, so it is not hidden when allauth
is absent. Today the Account Center group this package adds is built only when allauth is
installed, so the build has to place the tokens entry without relying on that.

**ADR:** none, covered by the decision record D1 requires.

## D4 — Tokens have a name and a chosen lifetime, and no last-used time

knox's token record holds a hash, the first characters of the token, the owner, a creation time
and an expiry. It has no name and no last-used time.

The maintainer's review settled two of the three. Naming a token is standard practice and is how a
person knows what they made each one for, so tokens are named (D11). A person also has to be able
to say when a token expires, so creating one asks for a lifetime (D12).

A last-used time stays out. Recording it would mean writing on every API request, which is knox's
job and not this package's, and the package checks no request.

`CONTEXT.md` currently says a person can "see when each was last used". That was written before
the backend was read closely, and the spec corrects it (FR-013).

**ADR:** none here. The name is recorded under D11.

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

## D11 — The name is kept in a model of the package's own, beside knox's record

A name has to be stored somewhere and knox has no field for it. There are two ways to add one.
Swapping knox's token model for one with a name is what knox offers, and Article XII rules it out
("never subclasses one of their models"). A swapped model is also hard to adopt: a project has to
choose it before its first migration. So the package keeps the name in one small model of its own,
with a one-to-one link to whichever knox token model is active and a cascade, so the name goes when
the token does. It holds nothing else.

This is the package's first model. Article IX applies: both fields carry a verbose name and help
text, the link's own unique index is the only lookup path, the name is never searched or ordered
by and is not indexed, and the feature adds one migration.

A token made outside the tokens page has no row. It is listed as having no name, so it can still
be seen and revoked. Names are not unique: two tokens with one name are a person's own business.

Article XII says a gap upstream is raised there first. A name on a token is something knox could
reasonably grow. Whether to propose it is the maintainer's call, and the decision record says the
model can be dropped if knox gains one.

**ADR:** required, the same record D1 requires (FR-014).

## D12 — A person chooses a lifetime from a short fixed list

Creating a token asks for its lifetime: 7 days, 30 days, 90 days, 1 year, or never. 30 days is
selected to begin with, so a person who does not think about it gets a token that expires. The
list is fixed in the package. Making it a setting is left until a project asks, under Article II.

The choice is passed to knox as the token's expiry. knox's `TOKEN_TTL` setting is therefore not
used for these tokens. It still decides the lifetime of tokens knox's own views create. The limit
per person is unchanged and still knox's setting (D7).

A list and not a date field, because a person choosing a lifetime is choosing roughly how long,
and a list cannot produce a date in the past. Offering "never" is deliberate: a long-running
script is the case the feature exists for, and the alternative is a person re-issuing tokens by
hand or choosing the longest option without thinking.

**ADR:** none, local to one form.

## D13 — The list shows no part of the token, and days without a time

With a name on every token made here, the first characters of the token no longer do any work in
the list, and showing them puts a piece of a secret on a page for no reason. The list shows the
name, the day the token was created and the day it expires. The time of day is left out: it made
the table cramped, and the shortest lifetime on offer is a week.

**ADR:** none.

## D14 — One setting says who may hold tokens

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
