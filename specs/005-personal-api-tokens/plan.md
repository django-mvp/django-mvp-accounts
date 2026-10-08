# Implementation Plan: Personal API tokens

**Branch**: `005-personal-api-tokens` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Prototype**: [sketch.md](sketch.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

django-rest-knox keeps tokens and has no browser pages, so this feature adds three account
management pages over knox's own records: a list, a create form and a revoke confirmation
(research R1, R2). The maintainer approved their templates as a prototype, and those stay as they
are. The Python behind them is removed and rebuilt test-first.

The pages live in a subpackage, `mvp_accounts/tokens/`, that only a project routing them ever
imports, so knox and Django REST framework are never imported anywhere else (R6). A new token's
value reaches the one page that shows it in a signed, short-lived cookie, so the server stores
nothing (R3). A token is named in an address by knox's own `token_key` (R4). One setting names a
function that says who may hold tokens, read in one place (R7). The package adds no model and no
migration.

Naming tokens is not built. Research answers the planning note with a recommendation for the
maintainer (research, "Planning notes").

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2, 6.0 and 6.1
**Primary Dependencies**: django-mvp ≥ 0.27.0 (runtime, unchanged). New optional extra `api`: Django REST framework 3.x ≥ 3.16 and django-rest-knox 5.x (R8)
**Storage**: none in the package. The demo gains knox's token table
**Testing**: pytest, pytest-django, xdist. Views driven through the test client, tokens checked against a real API request in the demo
**Target Platform**: any Django project built on django-mvp
**Project Type**: reusable Django app
**Constraints**: nothing from knox or Django REST framework imported outside `mvp_accounts/tokens/views.py` and what only it imports; no model, no migration; every added string translatable; the approved templates keep their markup and words
**Scale/Scope**: 3 views, 1 form, 1 access function, 1 template tag, 1 menu entry, 1 card, 3 page templates and 1 component (already written), 1 decision record

## Constitution Check

| Article | How this plan meets it |
|---|---|
| I Test-first | The prototype's Python is deleted first (T001). Every view, form, function, entry and card comes back behind a failing test |
| II Simplicity | Three class-based views, one form, one function. No registry, no settings object, no system check. Lifetimes are a fixed list (D11) |
| III Anti-abstraction | One small mixin shared by the three views for sign-in and access. Nothing else is shared ahead of a second caller |
| IV Integration-first | Tests create real knox tokens and send them to the demo's API endpoint |
| V Security | Every query starts from the signed-in person's own tokens. The complete token is never stored by the package and its page is not cached (R3). State changes are POSTs under Django's CSRF protection. Token values are escaped by the template engine |
| VI Documentation | README section, `CONTEXT.md` correction, CHANGELOG and ADR 0005, each in the story that introduces what it describes |
| VII Dependencies | Two optional dependencies, bounded to the majors the suite runs, in an extra and never at runtime (R8) |
| VIII i18n | Every string wrapped, catalogue regenerated in the last story (R10) |
| IX Data model | No models (FR-012) |
| X Tests | Mirrored modules under `tests/test_tokens/` and `tests/test_templatetags/`. One factory for knox's token. The subprocess run and the component test are declared in `non-mirror-paths` (R9) |
| XII Upstream does the work | knox creates, hashes, expires and checks tokens. The pages are built here because knox has none, and ADR 0005 records it. knox's model is neither subclassed nor swapped |
| XIII Optional capabilities | Without knox, or without Django REST framework: the package imports, the Account Center renders, and there is no entry, card or page. A subprocess test asserts each (R6) |
| XIV Scope | The access setting asks the project who gets the pages. The package decides nothing about what a person or a token may do (D13) |

No violations.

## Design

### Layout

```text
mvp_accounts/
  menus.py                       the "Account" group, now built with or without allauth
  templatetags/mvp_accounts.py   may_use_api_tokens, for the landing page's card
  tokens/
    access.py                    may_use_tokens(user): the one reader of the setting
    forms.py                     CreateTokenForm: the lifetime choice
    urls.py                      three routes, included by the host project
    views.py                     TokensView, CreateTokenView, RevokeTokenView
  templates/
    mvp/account/overview.html                      the card
    mvp_accounts/tokens/{list,create,revoke}.html  the approved pages
    cotton/mvp_accounts/token/created.html         the approved one-time card
demo/
  api.py                         the one API endpoint, apart from demo/views.py (R6)
  access.py                      staff_only, the demo's answer to who may hold tokens
```

`mvp_accounts/tokens/` is a plain subpackage. It is not an installed app.

### Routes

| Name | Path under the include | View |
|---|---|---|
| `account_api_tokens` | `` | `TokensView` |
| `account_api_token_create` | `create/` | `CreateTokenView` |
| `account_api_token_revoke` | `<str:token_key>/revoke/` | `RevokeTokenView` |

### Views

All three share `TokenPageMixin`: `LoginRequiredMixin` first, then `PermissionDenied` for a
signed-in person `may_use_tokens` turns away (R5, R7).

One module-level function, `working_tokens(user)`, returns that person's tokens with no expiry or
an expiry in the future, newest first (R1). Every view starts from it, so no view can reach
another person's token or an expired one. `at_limit(user)` compares its count with knox's
`TOKEN_LIMIT_PER_USER`.

- **`TokensView`** (`MVPTemplateView`, never cached). Context: `tokens`, `token_limit`,
  `at_limit`, `header_prefix`, and `new_token` when the signed cookie is present: a mapping with
  the `value` and its `token_key`. Reading the cookie deletes it on the same response (R3).
- **`CreateTokenView`** (`PageMixin` + Django's `FormView`). At the limit, loaded or submitted, it
  adds an error message and redirects to the list. A valid form creates the token through knox's
  manager with the chosen expiry and redirects to the list with the signed cookie set (R1, R3).
- **`RevokeTokenView`** (`MVPTemplateView`). Looks the token up by `token_key` among the person's
  working tokens. Nothing found, on GET or POST: a message and a redirect to the list. GET renders
  the confirmation. POST deletes and redirects with a success message (R4, R5).

The templates read `token.token_key`, `token.created` and `token.expiry`, and compare
`new_token.token_key` with each row's for the "New" badge. The prototype's templates compared
digests and built the revoke link from the digest. Those two expressions change to `token_key`.
Nothing a person sees changes.

### The one-time token

Set on the redirect from `CreateTokenView`, read and deleted by `TokensView` (R3):

| Attribute | Value |
|---|---|
| name | `mvp_accounts_new_token` |
| value | the complete token, signed with a salt of the package's own |
| `max_age` | 60 seconds, checked again when read |
| `path` | the tokens page's own path |
| `httponly`, `samesite="Strict"` | always |
| `secure` | when the request is secure |

### Turning it on

The entry is one more child of the "Account" group in `mvp_accounts/menus.py`, with a `check` that
calls `may_use_tokens` and `pages` naming the create and revoke routes so it stays current on
them. The group is appended whether or not allauth is installed (R6). The card is added to the
landing page template behind `{% url %}` and the `may_use_api_tokens` tag.

ADR 0002 says `menus.py` adds nothing unless allauth is installed. ADR 0005 records the change:
the group now exists for the tokens entry too, and is still not drawn when it has nothing to show.

### Token names

Not built (research, "Planning notes"). The plan leaves room: one queryset function feeds every
page, and the create form has one field.

## Story order

**US1 → US3 → US2 → US4 → US5, one at a time, in one working tree.** The stories share
`views.py`, `menus.py` and the demo, so they are built in sequence on the feature branch. US1
makes the tokens page reachable, US3 makes it list, US2 creates, US4 revokes, and US5 then closes
all of it to the people a project shuts out.

T001 is foundational and is done before any story: it removes the prototype's untested Python so
that every later task starts red.

## Risks

- **A stale `KNOX_TOKEN_MODEL`.** A project that swapped knox's model is served by
  `get_token_model()`. The suite runs knox's own model only.
- **The cookie on an insecure origin.** `secure` follows the request, so the demo on plain HTTP
  still works. `samesite="Strict"` holds because the redirect is same-site.
- **The clipboard on plain HTTP.** The approved component falls back when the clipboard API is
  absent. It is a browser behaviour and has no test. It is on the walkthrough.
