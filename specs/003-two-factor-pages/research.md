# Research — 003 Two-factor authentication

Every claim below was read from the installed django-allauth 65.19.4
(`.venv/lib/python3.13/site-packages/allauth/`) and django-mvp 0.25.0, not from documentation.

## R1 — Every multi-factor page already lands on one of FS-001's two layouts

- `mfa/base_entrance.html` extends `allauth/layouts/entrance.html`, and `mfa/base_manage.html`
  extends `allauth/layouts/manage.html`. Both layouts are overridden by FS-001.
- Entrance: `mfa/authenticate.html` (the second-factor step) and `mfa/trust.html`.
- Management: `mfa/index.html`, `mfa/totp/*`, `mfa/recovery_codes/*`, `mfa/webauthn/*` except
  `signup_form.html`.
- `mfa/reauthenticate.html` and `mfa/webauthn/reauthenticate.html` extend
  `account/base_reauthenticate.html`, which extends `account/base_entrance.html`. FS-001 overrides
  that file to pick the management layout for a signed-in person, so re-authentication is a
  management page with no new work.
- `mfa/webauthn/signup_form.html` and `account/signup_by_passkey.html` extend
  `account/base_entrance.html`. The person is not signed in during passkey sign-up, so both draw as
  entrance pages.

So the feature overrides **no page template**. What the layouts do not reach is the elements the
multi-factor pages use and FS-001 never needed (R2), and the ids those elements drop (R3).

## R2 — Elements the multi-factor pages use that FS-001 does not override

| Element | Used by | allauth's own markup |
|---|---|---|
| `panel` | `mfa/index.html` | bare `<section><h2>` with actions in a `<ul>` (`allauth/elements/panel.html`) |
| `img` | `mfa/totp/activate_form.html` (the QR code) | bare `<img src alt>` |
| `table`, `thead`, `tbody`, `tr`, `th`, `td` | `mfa/webauthn/authenticator_list.html` | bare table tags |

`index.html` fills `panel`'s `actions` slot more than once. Repeated slots collect into a list,
and `{% slot actions %}` renders them all, joined (`allauth/templatetags/allauth.py:50-61`). The
override only iterates `slots.actions` if each action needs its own wrapper.

## R3 — Ids and data attributes allauth's scripts look up

`mfa/static/mfa/js/webauthn.js`, `recovery_codes.js` and `account/static/account/js/onload.js`:

- `onload.js` runs every `<script data-allauth-onload="allauth.…" type="application/json">` and
  passes it the JSON body. The JSON's `ids` object names every element the script then finds with
  `getElementById`. That JSON is written by allauth's page templates, which this feature does not
  override, so the ids *named* are always allauth's. What the reskin can break is the elements
  *carrying* them.
- Per page, the ids named and the element that must carry each:

| Page | Ids | Carried by |
|---|---|---|
| second-factor step (`mfa/authenticate.html`, webauthn enabled) | `mfa_webauthn_authenticate`, credential `auto_id`, `js_data`; and `webauthn_form` as a `form=` target | `button`, crispy hidden input, `json_script`, **`form` element's `id`** |
| add security key | `mfa_webauthn_add`, `passwordless` and `credential` `auto_id`s, `js_data` | `button`, crispy inputs, `json_script` |
| passkey sign-up (`mfa/webauthn/signup_form.html`) | `mfa_webauthn_signup`, credential `auto_id`, `js_data` | `button`, crispy input, `json_script` |
| security-key re-authentication | `mfa_webauthn_reauthenticate`, credential `auto_id`, `js_data` | `button`, crispy input, `json_script` |
| sign-in page, passkey sign-in | `passkey_login` (with `form="mfa_login"`), `mfa_credential` | `button`, allauth's literal `<form id="mfa_login">` in `mfa/webauthn/snippets/login_script.html` |
| recovery codes | `recovery_codes`, `codes_saved` (only with `MFA_RECOVERY_CODES_SHOW_ONCE`) | **`field` element** |

- FS-001's `button` element already writes `id` and `form` (both non-`href` branches).
- FS-001's `form` element writes no `id`. `authenticateForm` finds the form through
  `credentialInput.closest('form')`, so the script itself survives, but the "Use a security key"
  button carries `form="webauthn_form"` and FR-005 requires the id kept. The `form` element gains
  `id`.
- FS-001's `field` element does not handle `type="textarea"`, `readonly`, `rows` or a `value` slot,
  all of which the recovery-codes page passes. django-mvp's `<c-form.field>` renders
  `type="textarea"` with the default slot as its content and passes `readonly`/`rows` through
  (`mvp/templates/cotton/form/field.html`).
- The credential and passwordless inputs come from crispy through django-mvp's `<c-form.render>`
  (`cotton/form/render.html`), which keeps each field's `auto_id`. FR-005 depends on that.
- `webauthn.js` reads `credentialInput.closest('form')` and `loginBtn.form`. Both need the input
  and the button inside, or linked to, a real `<form>`.

The generic test for FR-005 / SC-002: for every `script[data-allauth-onload]` on the page, parse its
JSON, and assert that every value in `ids` is the `id` of an element on the page. The
recovery-codes page names `codes_saved` unconditionally but draws it only with
`MFA_RECOVERY_CODES_SHOW_ONCE`, and the script tolerates its absence, so on that page the check runs
under that setting only.

## R4 — The QR code has no background of its own

`mfa/adapter.py:89` builds it with `qrcode.image.svg.SvgPathImage`: one `<path>` filled black on a
transparent canvas, handed to the template as a base64 `data:image/svg+xml` URI. On a dark theme
the black modules sit on the page's dark background. The `img` override therefore puts the image
on `bg-white` (Tailwind's fixed white, not a theme colour) with padding for the quiet zone. The
contract a test can hold: the QR `<img>` carries `bg-white`, and the SVG it shows fills its
modules with a dark colour.

## R5 — Settings and their constraints

- `MFA_SUPPORTED_TYPES` defaults to `["recovery_codes", "totp"]`. The demo adds `"webauthn"`.
- `MFA_PASSKEY_LOGIN_ENABLED` needs `webauthn` in the supported types. No other constraint.
- `MFA_TRUST_ENABLED` adds the "trust this browser" stage.
- **`MFA_PASSKEY_SIGNUP_ENABLED` fails system checks (`mfa/checks.py`, `Critical`) unless
  `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`
  and `email*` is a signup field.** The demo keeps `ACCOUNT_EMAIL_VERIFICATION = "optional"`
  (decisions.md D5), so passkey sign-up is tested under settings overrides and is off in the demo.
- `MFA_TOTP_INSECURE_BYPASS_CODE` is accepted only with `DEBUG` on (`mfa/app_settings.py:71`,
  raises `ImproperlyConfigured` otherwise). The demo sets it so the walkthrough needs no phone
  (D6). `tests/settings.py` resets it to `None`, so every test enters a real code.
- `AddWebAuthnForm.passwordless` exists only when `MFA_PASSKEY_LOGIN_ENABLED` is on when the forms
  module is imported (`mfa/webauthn/forms.py:55-63`). The suite inherits the demo's `True`.
- Turning on `allauth.mfa` and passkey sign-in adds a passkey button and a `data-allauth-onload`
  script to every sign-in page, so FS-001's entrance-page tests are re-run in T001.
- `allauth.mfa` requires `qrcode` and `fido2`, shipped as the `mfa` extra. Neither is installed
  today. The development group changes to `django-allauth[mfa]`. The package's runtime dependencies
  do not change (FR-009).

## R6 — Which pages allauth routes follows the settings at import time

`allauth/mfa/urls.py` includes the webauthn routes only when `webauthn` is supported, and
`account_signup_by_passkey` exists only with passkey sign-up on. `allauth/mfa/webauthn/urls.py:34-38`
adds `mfa_login_webauthn` and `mfa_signup_webauthn` the same way. Tests that switch either use
FS-001's `rebuild_urls` fixture, which must reload `allauth.mfa.webauthn.urls` and `allauth.mfa.urls`,
in that order, ahead of `allauth.urls`: it reloads neither today. `mfa_index` resolves whenever `allauth.mfa` is installed, which is
what the Account Center entry and card follow (ADR 0002).

## R7 — Producing factor state in tests

- TOTP: `allauth.mfa.totp.internal.auth.TOTP.activate(user, secret)`; the current code is
  `format_hotp_value(hotp_value(secret, next(yield_hotp_counters_from_time())))`. A code used to
  sign in is refused a second time within its period (`totp/internal/auth.py:100-121`).
- Recovery codes: `allauth.mfa.recovery_codes.internal.auth.RecoveryCodes.activate(user)`, then
  `.get_unused_codes()`.
- Security keys: an `allauth.mfa.models.Authenticator` of type `WEBAUTHN` whose `data` carries a
  `name` and a `credential`. The list page reads `wrap.is_passwordless`, from the credential's
  `clientExtensionResults.credProps.rk`. Every page that begins an authentication or registration
  (the second-factor step, adding a key, re-authentication) runs `parse_registration_response` on
  every stored credential (`webauthn/internal/auth.py:109-118, 208-212`), so the stored credential
  must be a registration response that parses: a recorded fixture or one built with fido2's own
  constructors. One factory in `tests/factories.py` (Article X), verified by rendering
  `mfa_list_webauthn` and `mfa_reauthenticate_webauthn`.
