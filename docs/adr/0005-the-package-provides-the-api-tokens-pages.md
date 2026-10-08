# ADR 0005 — The package provides the API tokens pages itself

**Status:** accepted

## Decision

django-rest-knox keeps API tokens, and this package provides the browser pages for them: a list
of a person's tokens, a page to create one and a page to revoke one. The pages are limited to
those three actions over knox's own records.

- The package adds no model, no migration and no installed app. `mvp_accounts/tokens/` is a plain
  subpackage, and a token is named in an address by knox's own `token_key`. Tokens have no names.
- The pages exist in a host project that installs the `api` extra, adds `knox` to
  `INSTALLED_APPS` and includes `mvp_accounts.tokens.urls`. Nothing else in the package imports
  knox or Django REST framework except the pages themselves, which only a project that routes them
  ever loads. A project with neither installed gets a package that
  imports, an Account Center that renders, and no API tokens entry or card.
- The API tokens entry follows the pages: it is drawn when the tokens URLs resolve, the same rule
  [ADR 0002](0002-account-management-lives-in-the-account-center.md) uses for allauth's pages.
- The "Account" group in `mvp_accounts/menus.py` is now built whether or not allauth is
  installed, because the API tokens entry needs nothing from allauth. It holds allauth's entries
  and the re-authentication pages only when allauth is installed, and the API tokens entry last.
  A group with no visible entry is still not drawn.
- A host project says who may hold tokens through one setting, `MVP_ACCOUNTS_API_TOKEN_ACCESS`,
  that names a function of its own. The setting is read in one function, and the pages, the entry
  and the card all ask it. With no setting, every signed-in person may. The package decides
  nothing about what a person or a token may do.
- A new token's complete value is carried from the create page to the tokens page in a signed,
  short-lived cookie that the tokens page deletes as it shows the value. The package never writes
  the value to the session or the database.

## Why

knox ships three API views (sign in, sign out, sign out everywhere), an admin registration and no
templates, so there is nothing to restyle as there is for allauth. Without pages the only
way to see a token is the admin, which is for staff, so every host project would build the same
three pages. Building them once here keeps the work in the package whose job is account
management.

Keeping to three actions keeps knox the owner of what a token is. It creates, hashes, expires and
checks tokens, and the pages call its manager and query its model. Naming tokens or showing when
one was last used would need a table of this package's own, with a migration every host project
would have to run, and is left out for that reason.

Who gets API access differs between sites, and only the host project knows. Asking it one
question keeps permissions, roles and groups where they belong, in the host project, while still
letting a site keep the pages from people who must not have them.

A token is worth as much as a password, so its value is shown once and stored nowhere by this
package. The session would have written it to the database, and showing it in the reply to the
form would have created a second token on a reload.

The tokens pages need a signed-in person and the Account Center and nothing from allauth, and this
package is not tied to one authentication package. Gating the group on allauth would hide the
pages from a project that has none.

## Revisit if

knox ships browser pages of its own, or a second token package has to be supported. Also if tokens
need data knox does not keep, such as a name or a last-used time, which would mean a model of this
package's own.
