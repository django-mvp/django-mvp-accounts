# Research — 005 Personal API tokens

Every claim about django-rest-knox cites the installed package, django-rest-knox 5.1.0, under
`.venv/lib/python3.13/site-packages/knox/`. Claims about django-mvp cite django-mvp 0.27.1 under
`.venv/lib/python3.13/site-packages/mvp/`. Paths below are relative to those directories unless
they start with `mvp_accounts/`, `demo/` or `tests/`. Django REST framework is 3.18.3 and Django
is 6.1.1 in the development environment.

The branch already carries the approved prototype. Its templates, markup and words stay. Its
Python is untested and is rebuilt here, test-first.

## Planning notes

### A way to name a token

**Not adopted in this build. Raised at review and at the merge decision, with a recommendation.**

The maintainer wants a person to be able to name a token, and has ruled that whether the package
gains a model or an app of its own for it is decided in planning and review, not in a prototype
(`planning-notes.md`). The ways a name could be provided:

| Way | What it costs | Verdict |
|---|---|---|
| A field on knox's record | knox has none. Its record is `digest`, `token_key`, `user`, `created`, `expiry` (`models.py:53-64`) | Not available |
| Swap knox's token model for one with a name | knox supports it (`models.py:71-73`, `KNOX_TOKEN_MODEL`). Article XII forbids subclassing an upstream model, and a swappable model has to be chosen before a project's first knox migration | Ruled out by the constitution |
| The per-token `prefix` knox's manager accepts | `AuthTokenManager.create(user, expiry, prefix)` (`models.py:31-46`) puts up to 10 characters (`settings.py:56`) on the front of the token, and they land in `token_key`. A "name" of 10 characters from a limited alphabet that becomes part of the secret itself | A workaround, not a name. Rejected |
| A model of this package's own, one-to-one with knox's active token model | One small table: a name and a link, deleted with the token. Needs a model, a migration and an app a project installs, which FR-012 and the maintainer's ruling keep out of this build. Tried in the prototype's second round, where it worked, with one catch: Django's migration writer reads a `KNOX_TOKEN_MODEL` setting that a project on knox's own model never defines, so the migration has to be written by hand | The only way that gives real names without replacing knox's model |
| Raise it upstream | A `name` or `description` on a token is a reasonable thing for knox to carry. Arrival is not in this package's hands | Worth doing, on its own timescale |

Nothing in this feature closes any of these off. The tokens pages read knox's records through one
queryset function, and the create form is one field, so a name can be added later as a form field,
a column and one related lookup.

**Recommendation for the maintainer:** take names as a follow-up feature built on the one-to-one
model, with its own specification change (FR-012 would have to allow one model) and decision
record, and raise the gap with django-rest-knox at the same time so the model can be dropped if
knox grows a name. It is the smallest thing that works on every project and replaces nothing of
knox's.

## What `sketch.md` asks of the build

Each line under "What the screens need from the code" and "What the prototype faked" is answered
by a section below: the one-time token (R3), the address of the confirmation page (R4), turning
the pages on and knox being absent (R6), refusals and messages (R5), the access setting (R7), the
tests that pin lists (R9), the extra's bounds (R8) and the documents (plan).

## R1 — What knox stores and how it is counted

`AbstractAuthToken` (`models.py:49-67`) has `digest` (the primary key, 128 characters),
`token_key` (indexed, the token's first 15 characters after any prefix, `settings.py:54`), `user`
(related name `auth_token_set`), `created` (`auto_now_add`) and `expiry` (nullable). The active
model is `knox.models.get_token_model()` (`models.py:76-93`).

`AuthTokenManager.create(user, expiry=_UNSET, prefix=None)` (`models.py:31-46`) returns
`(instance, token)`. An `expiry` left out takes `TOKEN_TTL`. A `timedelta` is added to now. `None`
stores no expiry. So a lifetime chosen on the page is passed straight through, and "never" is
`expiry=None`.

knox counts a person's working tokens as `Q(expiry__gt=now) | Q(expiry__isnull=True)`
(`views.py:69-73`) and compares the count with `TOKEN_LIMIT_PER_USER`, which is `None` by default
(`settings.py:12`). It does so only in its sign-in view, never in `create`. The pages use the same
filter for the list and for the limit (FR-009, FR-010, D6, D7).

knox authenticates by looking a token up by `token_key` and then comparing digests
(`auth.py:63`). `token_key` is therefore knox's own non-secret handle for a token, and it is what
knox's admin and this feature's list both show.

`AUTH_HEADER_PREFIX` is `"Token"` by default (`settings.py:16`). The new-token card reads it for
its "how to send it" line.

## R2 — The page machinery

`mvp.views.MVPTemplateView` is `PageMixin` plus Django's `TemplateView`. `PageMixin`
(`views/base.py:148-240`) supplies `page.title`, `page.subtitle` and `page.breadcrumbs` from
`page_title`, `page_subtitle` and `get_breadcrumbs()`. It is importable from `mvp.views.base`.
django-mvp's own form views resolve a model's metadata and refuse a plain `Form`, so the create
page is Django's `FormView` with `PageMixin`, and the list and confirmation pages are
`MVPTemplateView`.

A page joins the Account Center by extending `mvp/account/base.html` and by an
`AccountCenterMenu` entry, whose `check` callable hides it per request (`flex_menu/menu.py:358`).
A `MenuGroup` with no visible children is not drawn (`menus.py:92-100`), and django-mvp drops an
entry whose URL does not resolve.

`django-flex-menus` imports the `menus` module of every installed app (`flex_menu/apps.py:9`).
The tokens code is a subpackage of `mvp_accounts` and not an app, so its entry is declared in
`mvp_accounts/menus.py`.

## R3 — The one-time token and FR-008

The prototype put the new token in the session for one redirect. Django's default session store
is a database table, so the complete token would be written to disk, and would stay there if the
redirect were never followed. FR-008 and D9 rule that out.

Three ways to carry it:

| Way | Problem |
|---|---|
| Render the token in the response to the POST, with no redirect | A reload re-submits the form and creates a second token, against the spec's edge case |
| The session, or Django messages falling back to it | Written to the server's storage |
| A signed cookie set on the redirect and deleted by the page that reads it | None found |

The build uses the cookie: `HttpResponse.set_signed_cookie` on the redirect, with a short
`max_age`, `httponly`, `samesite="Strict"`, `secure` following the request, and `path` set to the
tokens page. The tokens page reads it with `get_signed_cookie` (same `max_age`), shows the value
and deletes the cookie on that response. The server stores nothing. The only copy outside knox's
hash is in the browser the token is being handed to, for one request. A reload finds no cookie:
no value, no second token.

The page that shows the value is sent with `never_cache`, so a browser or proxy does not keep a
copy of the page either.

The "New" badge needs to know which row was just created. `token_key` is the first 15 characters
of the value (`CONSTANTS.TOKEN_KEY_LENGTH`), so the row is found from the value itself and nothing
else has to travel.

## R4 — What names a token in an address

knox's primary key is the stored hash. The prototype put it in the confirmation page's address.
The build uses `token_key`: it is what the list already shows the person, it is knox's own lookup
handle (R1), and it is indexed. Every lookup is scoped to the signed-in person's working tokens
first, so a `token_key` that belongs to someone else finds nothing.

Two of one person's tokens sharing 15 random characters is not a case worth a branch. The lookup
is a filter, and revoking deletes what it finds.

A project's `TOKEN_PREFIX` may hold characters that need quoting in a path. `reverse()` quotes
them and Django's `str` converter unquotes them.

## R5 — Refusals and messages

- **Not signed in:** `LoginRequiredMixin` sends the visitor to sign in (FR-006).
- **Signed in, not allowed to hold tokens:** `PermissionDenied`, a 403, as the maintainer approved
  (FR-019).
- **At the limit:** the create page, loaded or submitted, creates nothing and returns to the
  tokens page with an error message. The notice above the list is what stays on screen (FR-009).
- **A token that is gone, expired or someone else's:** the confirmation page, loaded or submitted,
  deletes nothing and returns to the tokens page with a message that the token no longer exists.
  One response for all three, so nothing tells a stranger's token from a missing one (US4
  scenario 5, and the edge case on a token already gone).
- **Revoking by following a link:** the confirmation page is a GET and changes nothing. Only its
  form's POST deletes (US4 scenario 6).

Messages are asserted by level and by having been added, never by wording
(`docs/contributing/standards/testing.md`, "Text").

## R6 — Turning it on, and knox being absent

The pages exist when the project includes `mvp_accounts.tokens.urls`. That module imports the
views, which import knox, so knox is imported only in a project that routes the pages. Everything
the rest of the package touches at import time must stay free of knox and Django REST framework:
`mvp_accounts/menus.py`, the template tag the landing page's card uses, and the access check they
both call. The access check reads a Django setting and nothing else.

The entry and the card follow `{% url %}` and django-mvp's own dropping of an unrouted entry, the
rule ADR 0002 uses for allauth's pages. Until now `mvp_accounts/menus.py` built its "Account"
group only when allauth is installed. The tokens entry must not need allauth (FR-005, D3), so the
group is built either way: with allauth's entries when allauth is installed, and the tokens entry
always. Unrouted, the entry is dropped, and a group left empty is not drawn (R2).

Proving absence needs a process where knox cannot be imported. The suite already runs a script in
a subprocess under other settings (`tests/conftest.py`, `run_in_subprocess`). Setting
`sys.modules["knox"] = None` and `sys.modules["rest_framework"] = None` before `django.setup()`
makes any import of either raise, which is what an uninstalled package does. A second run blocks
knox alone, for a project with Django REST framework and no knox (US1 scenario 3).

The demo's API view imports Django REST framework. It moves out of `demo/views.py` into a module
of its own, so the settings and routes used by those subprocess runs can leave it out.

## R7 — The setting that says who may hold tokens

One setting, `MVP_ACCOUNTS_API_TOKEN_ACCESS`, holding a dotted path to a callable that takes the
user and returns a truthy value when they may hold tokens. It is read in one function,
`mvp_accounts.tokens.access.may_use_tokens`, which the views, the menu entry's `check` and the
card's template tag all call. Unset, every signed-in person may. A person who is not signed in
never may.

The name follows the package (`MVP_ACCOUNTS_`), then the thing (`API_TOKEN`), then what it decides
(`ACCESS`, the glossary's word for reaching your own account). The path is resolved with Django's
`import_string`, which caches the import and raises an `ImportError` naming the path when it is
wrong. No system check is added (FR-012, and the README's "nothing is checked for you").

## R8 — The install extra

`[project.optional-dependencies] api = ["djangorestframework>=3.16,<4", "django-rest-knox>=5.0,<6"]`.
Django REST framework 3.16 is the first release that supports Django 5.2, the oldest Django this
package supports, and 3.x is the major the suite runs (3.18.3). knox 5.x is the major the suite
runs (5.1.0). The development group installs the extra through the package's own name, so the
suite and the demo always run what the extra resolves.

`deptry` reports Django REST framework as unused, because only knox is imported. It is named in
the extra so both arrive at tested versions, and is listed under `DEP002`.

## R9 — Tests

- **Mirrored modules.** `mvp_accounts/tokens/access.py`, `forms.py`, `views.py` and `urls.py`
  mirror to `tests/test_tokens/`. `mvp_accounts/templatetags/mvp_accounts.py` mirrors to
  `tests/test_templatetags/test_mvp_accounts.py`. `mvp_accounts/menus.py` stays with
  `tests/test_menus.py`.
- **Not mirrored**, declared in `non-mirror-paths`: `tests/test_without_knox.py` (a startup, in a
  subprocess) and the component's test in `tests/test_components/`.
- **Three existing tests pin lists that grow**: `tests/test_apps.py` (the "Account" group's
  children), `tests/test_without_allauth.py` (no "account" group without allauth, which is no
  longer the rule) and `tests/test_app.py` (the package's components). Each is updated by the task
  that changes what it pins.
- **Factory.** knox's token is a model the tests build, so it gets one factory,
  `AuthTokenFactory`, that goes through knox's manager and can return the complete value.
- **A real request.** FR-016's endpoint lets a test send a token to the demo's API and read who it
  was answered as, before and after revoking (US2 scenario 3, US4 scenarios 2 and 3).
- **Query count.** The tokens page is a list page: one token and several must cost the same number
  of queries.
- **No test of wording or appearance.** Rows are found by `token_key`, dates by the value's own
  formatted date, forms by field name, messages by level.

## R10 — Translations

`mvp_accounts/locale/en/LC_MESSAGES/django.po` is regenerated with `makemessages -l en` from
inside `mvp_accounts/`, as FS-004 did. Template strings use `{% trans %}` and `{% blocktrans %}`,
Python strings `gettext_lazy`.
