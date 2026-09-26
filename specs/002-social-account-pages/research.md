# Research — 002 Sign in with social accounts

Every claim about allauth cites the installed package, django-allauth 65.19.4, under
`.venv/lib/python3.13/site-packages/allauth/`. Paths below are relative to that directory unless
they start with `mvp_accounts/` or `mvp/`.

## R1 — Which pages the social account app renders, and what they extend

| Page | Template | Extends |
|---|---|---|
| Confirm sign-in or connect | `socialaccount/login.html` | `socialaccount/base_entrance.html` |
| Extra sign-up step | `socialaccount/signup.html` | `socialaccount/base_entrance.html` |
| Sign-in cancelled | `socialaccount/login_cancelled.html` | `socialaccount/base_entrance.html` |
| Sign-in failed | `socialaccount/authentication_error.html` | `socialaccount/base_entrance.html` |
| Connected accounts | `socialaccount/connections.html` | `socialaccount/base_manage.html` |
| Same-site redirect | `socialaccount/login_redirect.html` | nothing, a bare HTML document |
| Test provider's form | `dummy/authenticate_form.html` | `socialaccount/base_entrance.html` |

`socialaccount/base_entrance.html` is one line, `{% extends "allauth/layouts/entrance.html" %}`,
and `socialaccount/base_manage.html` is `{% extends "allauth/layouts/manage.html" %}`. FS-001
already overrides both layouts (`mvp_accounts/templates/allauth/layouts/`), so every page in the
table except `login_redirect.html` renders inside the shell with no new template. FR-001 to FR-003
are met for those pages by FS-001's layouts, and this feature's work there is tests.

The social account app's entrance base goes straight to the entrance layout. It does not pass
through `account/base_entrance.html`, which FS-001 made follow the visitor. So the confirmation
page renders as an entrance page even for a signed-in person connecting another account, which is
what FR-002 asks for.

`login_redirect.html` is rendered only by the OAuth2 callback when `SESSION_COOKIE_SAMESITE` is
`"Strict"` and the request is a GET without `_redir` (`socialaccount/providers/oauth2/views.py:176-194`,
called at `:206`). It is a zero-second `<meta http-equiv="refresh">` with a "Continue" link. It is
a page the app renders, so FR-001 covers it, and it needs a page-level override because it extends
nothing.

## R2 — How provider buttons are drawn

`account/login.html:53` and `account/signup.html:43` include `socialaccount/snippets/login.html`,
which reads `{% get_providers %}` and draws nothing at all when the list is empty
(`socialaccount/snippets/login.html:4-5`). With providers, it draws allauth's `hr` and `h2`
elements, then `socialaccount/snippets/provider_list.html`. The connections page includes the same
list with `process="connect"` (`socialaccount/connections.html:51`).

`provider_list.html` wraps the buttons in `{% element provider_list %}` and draws each with
`{% element provider name=… provider_id=… href=… %}`. For OpenID it draws one button per brand,
each with `provider_id` still `openid` (`socialaccount/snippets/provider_list.html:6-10`). allauth's
own elements are a bare `<ul>` (`templates/allauth/elements/provider_list.html`) and
`<li><a title=… href=…>name</a></li>` (`templates/allauth/elements/provider.html`). FS-001 overrides
neither.

So FR-004 and FR-005 are two element overrides: `provider_list` and `provider`. The provider id
reaches the element as `attrs.provider_id` and the display name as `attrs.name`. django-mvp's
`<c-button>` already takes an `icon` attribute and renders `<c-icon name="…">` inside the button
(`mvp/templates/cotton/button.html`), so the provider element passes the id as the button's icon
and the name as its text.

`get_providers` takes the list from the social account adapter's `list_providers`
(`socialaccount/templatetags/socialaccount.py:73-89`). A provider class with `uses_apps = True`
appears only when an app is configured for it. The test provider has `uses_apps = False`
(`socialaccount/providers/dummy/provider.py:23`) and appears whenever it is installed
(`socialaccount/adapter.py:246-264`).

## R3 — The refusal to disconnect is an error nothing draws

`DisconnectForm.clean` calls `validate_disconnect` (`socialaccount/forms.py:58-63`), which raises
a validation error when the account is the last one and the person has no usable password, or no
verified address under mandatory verification (`socialaccount/internal/flows/connect.py:18-41`).
Raised from `clean`, it is a non-field error.

Neither allauth's connections page nor any element draws non-field errors. The page draws each
account as a hand-built radio `field` and never calls `fields` (`socialaccount/connections.html:17-39`).
allauth's own `form` element draws only its two slots (`templates/allauth/elements/form.html`), and
so does FS-001's (`mvp_accounts/templates/allauth/elements/form.html`). Pages that draw the whole
form through `fields` get non-field errors from crispy (`crispy_tailwind/templates/tailwind/errors.html`),
so drawing them in the `form` element would print them twice on every such page.

FR-008 therefore needs the connections page itself to draw `form.non_field_errors`. A template
named `socialaccount/connections.html` in this package can extend allauth's template of the same
name. Django skips the template that is doing the extending and finds the next one, which is how
`mvp_accounts/templates/mvp/account/overview.html` already chains onto django-mvp's. It adds to the
`content` block through `{{ block.super }}` and keeps all of allauth's markup.

## R4 — The Account Center entry and card

allauth routes the social account app only when `allauth.socialaccount` is installed
(`urls.py:38`, `app_settings.py:28`). FS-001's rule applies unchanged: a menu entry whose
`view_name` does not resolve is dropped by django-mvp, and each card is drawn only when
`{% url … as %}` gives it a URL (ADR 0002). So "Connected accounts" needs no guard of its own. It is
one more child of the "Account" group in `mvp_accounts/menus.py`, which is already added only when
`allauth` is installed, and one more card in `mvp_accounts/templates/mvp/account/overview.html`. An
`is_installed("allauth.socialaccount")` check would state the same fact a second time and add a
branch only a separate process could cover.

django-mvp's icon pack names `link` (and `copy-link`) (`mvp/utils.py`), so the entry and card use
`link` without the project registering anything.

## R5 — Reaching every state in tests

- **Two providers**: the suite's settings add `allauth.socialaccount.providers.github` with an app
  configured in `SOCIALACCOUNT_PROVIDERS` (`"APPS": [{"client_id": …, "secret": …}]`), which
  `list_apps` reads without any database row. With the demo's test provider that makes two.
  django-mvp's icon pack already names `github`, and the demo maps `dummy`, so no icon is added for
  the suite.
- **No providers**: `get_adapter` imports `SOCIALACCOUNT_ADAPTER` on every call
  (`socialaccount/adapter.py:430-431`, `socialaccount/app_settings.py:131-135`), so a test adapter
  in `tests/adapters.py` whose `list_providers` returns an empty list, switched in with
  `override_settings`, empties the list for one test.
- **Confirm, extra sign-up step, cancelled, failed**: the test provider's own flow. Its login view
  renders the confirmation page on GET. Its form posts to `dummy_authenticate`, which completes a
  sign-in, or renders the cancelled page when the post carries `action=cancel`
  (`socialaccount/providers/dummy/views.py`). Leaving out the email address with `"email*"` in
  `ACCOUNT_SIGNUP_FIELDS` sends the visitor to the extra sign-up step. The failed page is
  `socialaccount_login_error`, reached only by its URL: cancel redirects to
  `socialaccount_login_cancelled` (`socialaccount/helpers.py:55-56`), and a missing or unknown
  state is a 403, not the failed page (`dummy/views.py:42-43`, `socialaccount/models.py:431-435`).
- **Same-site redirect**: a GET to the GitHub callback with `SESSION_COOKIE_SAMESITE="Strict"`.
- **Recent sign-in**: connecting and disconnecting both ask for re-authentication when
  `ACCOUNT_REAUTHENTICATION_REQUIRED` is on (`socialaccount/internal/flows/connect.py:45-46`,
  `:111`), and `force_login` records none, so those tests turn it off as `tests/test_elements.py`
  does. The refusal does not need to.
- **Refusal to disconnect**: a person with an unusable password and one connected account posts
  the disconnect form. The error is raised in `clean`, before re-authentication is asked for
  (`socialaccount/internal/flows/connect.py:44-46` runs only on save).
- **Social account app absent, allauth present**: which apps are installed is decided when Django
  starts, so it runs in a subprocess, as FS-001's no-allauth test does
  (`tests/test_without_allauth.py`). A settings module strips `allauth.socialaccount` and its
  providers and nothing else.

## R6 — The demo

`allauth.socialaccount` and `allauth.socialaccount.providers.dummy` join `INSTALLED_APPS` after
`allauth.account`. The social account app has models, so the demo database needs `migrate`, which
the README's demo steps already run. `EASY_ICONS["default"]["icons"]` gains `"dummy"`, mapped to a
Bootstrap icon like the demo's other names. `seed_demo` adds what the walkthrough needs to reach
every state without inventing a login:

- the staff account gets a connected test-provider account, so the connections page lists one
  and disconnecting it succeeds;
- a `social.user@example.com` account, following the fleet formula for a role, has no usable
  password and one connected test-provider account. Signing in with the test provider under that
  account's id reaches the refusal.
