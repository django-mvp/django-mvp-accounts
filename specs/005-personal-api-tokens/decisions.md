# Decisions — 005 Personal API tokens

The issue was specified without a round of questions to the maintainer. Each place where the issue
and the roadmap were silent is listed here with the reading chosen, so any of them can be
overruled on the specification's pull request.

## The reading the specification is built on

A person signed in to a site with a Django REST framework API opens an API tokens page in the
Account Center, creates a token and sees it once, sees the tokens they hold, and revokes any one
of them. django-rest-knox does everything to do with the token itself. This package provides the
page, because knox has none, plus the Account Center entry and card and an optional install extra.
A project that has not installed knox and routed the page gets nothing. The work serves G4, G2 and
G3, and it is the whole of roadmap item R5. No other issue cites R5.

## D1 — The package provides the tokens page itself

FS-001 to FS-004 restyled pages allauth draws. django-rest-knox 5.1 ships three API views (sign
in, sign out, sign out everywhere), an admin registration and no templates, so there is nothing to
restyle. R5's first deliverable is a page, so the package builds one.

Article XII says a feature upstream lacks is raised there first and building it here is recorded
under `docs/adr/`. A browser page for account management is outside what knox sets out to do, so
no upstream issue is proposed, and the spec requires the decision record (FR-014). The page is
kept to three actions over knox's own records: list, create, revoke.

**ADR:** required, written in the build (FR-014).

## D2 — knox being installed turns it on, and the project routes the page

The issue says a project without Django REST framework gets nothing. The page cannot work without
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

## D4 — No token names, no choice of lifetime, no last-used time

knox's token record holds a hash, the first characters of the token, the owner, a creation time
and an expiry. It has no name and no last-used time. Adding either means swapping knox's model for
one of ours, which Article XII rules out ("never subclasses one of their models"). A per-token
lifetime chosen by the person is possible with knox but adds a form and a judgement about what
lifetimes to offer, and Article II says to build what is needed now. Lifetime stays the project's
knox setting.

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
from a hijacked session lasts no longer than the project's knox lifetime allows and shows up in the
list, where it can be revoked. Left out, and named as an open risk on the pull request.

**ADR:** none.

## D9 — "Shown once" is a storage rule as well as a display rule

The spec says the package keeps the complete value in no lasting form (FR-008). How the value gets
from the create action to the one response that shows it is for planning, with that rule as the
constraint: nothing that survives that response may hold it.

**ADR:** none.

## D10 — The feature gets a prototype before it is planned

This is the first page in the package whose layout is the package's own. Every earlier page took
its structure from allauth. The list follows FS-004's sessions table and the entry and card use
slots that exist, but two things have no precedent to copy: how the one-time token is presented so
a person does not miss it, and how creating, the list and revoking sit together on one page. Those
are judgements for the maintainer's eye, and a test cannot settle them. The feature therefore
stops for a prototype review before any planning.

If the maintainer would rather treat it as a table and a button laid out like the sessions page,
the prototype can be skipped. Nothing in the spec depends on it.

**ADR:** none.
