# Tasks — 003 Two-factor authentication

**Branch**: `003-two-factor-pages` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green, and the work is committed. Documentation for a public name lands in the task
that introduces it. No test pins a design preference: button width, stacking, spacing and variant
are never asserted.

## Order

**US1 → US2 → US3, one at a time, in one working tree** (plan, *Story order*).

---

## US1 — Protect an account with an authenticator app and recovery codes (P1)

Issue: #19. Delivers FR-003, FR-004, FR-006, FR-009 to FR-011, US1's part of FR-001, FR-007 and
FR-008, and SC-003, SC-005 and the management half of SC-001.

### T001 — The multi-factor app in the demo and the suite

**Files**: `pyproject.toml`, `uv.lock`, `demo/settings.py`, `tests/settings.py`, `tests/test_demo.py`

Research R5. Development group: `django-allauth[mfa]>=65.19.4,<66`; `uv lock`. `allauth.mfa` after
`allauth.socialaccount` in the demo's `INSTALLED_APPS`. `MFA_SUPPORTED_TYPES = ["totp",
"recovery_codes", "webauthn"]`, `MFA_PASSKEY_LOGIN_ENABLED = True`, `MFA_TRUST_ENABLED = True`,
`MFA_TOTP_INSECURE_BYPASS_CODE` set to a fixed six-digit code. Comments say: passkey sign-up stays
off because allauth only allows it with mandatory email verification, which the demo does not use
(D5); the bypass code exists so the pages can be walked through without a phone, and allauth
refuses it without `DEBUG` (D6); security keys and passkeys need HTTPS or `localhost` (D3).
`tests/settings.py` sets `MFA_TOTP_INSECURE_BYPASS_CODE = None` with a comment saying every test
enters a real code. Tests: `mfa_index` resolves in the demo; the suite's bypass code is `None`.
Re-run FS-001's and FS-002's entrance-page tests: the sign-in page now carries the passkey button
and script, and any test counting its buttons needs a look.

### T002 — The Account Center entry and card

**Files**: `mvp_accounts/menus.py`, `mvp_accounts/templates/mvp/account/overview.html`,
`tests/test_menus.py`, `tests/test_account_center.py`

Plan, *Menu entry*. "Two-factor authentication" as the last child of the "Account" `MenuGroup`,
`view_name="mfa_index"`, icon `lock`, label through `gettext_lazy`. The docstring names it with the
other entries django-mvp drops when their view is not routed. Card after the connected accounts
card, drawn when `{% url "mfa_index" as … %}` resolves, with a translated sentence and a button to
the page. Tests: the entry's link, label and icon are in the Account Center; it follows "Connected
accounts" inside the same group; the card and its link are on the landing page (acceptance 1).

### T003 — The two-factor overview

**Files**: `mvp_accounts/templates/allauth/elements/panel.html`, `tests/test_elements.py`,
`tests/test_two_factor_pages.py`, `pyproject.toml` (`non-mirror-paths`)

Research R2. `panel` draws a `<c-card>` titled from the `title` slot, the `body` slot as its body,
and **every** entry of `slots.actions` in its footer. Element test: a panel with two actions draws
both. Page tests on `mfa_index` as a management page: with nothing set up, the authenticator app
panel offers "Activate" and the security-key panel "Add"; with TOTP and recovery codes set up, it
offers "Deactivate", and the recovery-code panel reports the unused count with View, Download and
Generate. With `MFA_SUPPORTED_TYPES=["recovery_codes", "webauthn"]` (rebuild the URLs), nothing on
the page links to `mfa_activate_totp` or names the authenticator app (acceptance 6, FR-007).

### T004 — Activating and deactivating the authenticator app

**Files**: `mvp_accounts/templates/allauth/elements/img.html`, `tests/test_elements.py`,
`tests/test_two_factor_pages.py`, `tests/factories.py`

Research R4, R7. `img` draws the image with `src` and `alt` escaped, on `bg-white` with padding,
and passes through nothing else allauth does not give it. Factory: `AuthenticatorFactory` with
TOTP and recovery-code traits built through allauth's own `TOTP.activate` and
`RecoveryCodes.activate`. Page tests on `mfa_activate_totp` as a management page: the QR `<img>`
carries `bg-white`, the stylesheet django-mvp serves defines `.bg-white`, and the image's SVG
(decoded from the data URI) fills its path with a dark colour (acceptance 3, SC-003); the secret is shown in the disabled `authenticator_secret` input; a wrong
code re-renders with allauth's error on the page (acceptance 4, FR-008); a correct code (a `tests/conftest.py`
helper computing `format_hotp_value(hotp_value(secret, next(yield_hotp_counters_from_time())))`,
reused by T008 and T010) activates and allauth's message appears in the shell. `mfa_deactivate_totp`
renders as a management page and deactivating shows allauth's message; with no other factor left,
allauth's message that two-factor authentication is off appears (edge case).

### T005 — Recovery codes

**Files**: `mvp_accounts/templates/allauth/elements/field.html`, `tests/test_elements.py`,
`tests/test_two_factor_pages.py`

Research R3. `field` gains a `textarea` branch drawing `<c-form.field type="textarea">` with `id`,
`readonly`, `rows` and the `value` slot as its content, keeping the label. Page tests:
`mfa_view_recovery_codes` is a management page listing every unused code inside
`<textarea id="recovery_codes" … readonly>`. Add the script-hook helper to `tests/conftest.py`
here (for every `script[data-allauth-onload]`, every id in its JSON is an element id on the page),
and run it on this page under `MFA_RECOVERY_CODES_SHOW_ONCE=True`, on the first view, where
`codes_saved` is drawn too (research R3). `mfa_download_recovery_codes` answers allauth's text file with the codes (acceptance 5).
`mfa_generate_recovery_codes` renders as a management page, and posting it replaces the codes and
shows allauth's message.

### T006 — Without the multi-factor app

**Files**: `tests/settings_without_mfa.py`, `tests/test_without_mfa.py`, `pyproject.toml`
(`non-mirror-paths`)

Same shape as `test_without_socialaccount.py`, through the `run_in_subprocess` fixture. With
`allauth.mfa` removed: the Account Center renders with no two-factor entry or card, the sign-in and
management pages render, and nothing raises (acceptance 2, SC-005). The test fails if pointed at
`tests.settings`.

### T007 — Documentation

**Files**: `README.md`, `CHANGELOG.md`, `mvp_accounts/locale/en/LC_MESSAGES/django.po`

README: a two-factor section saying which pages are reskinned once the host project installs
`allauth.mfa` (with allauth's `mfa` extra), that the package sets none of its settings, that the QR
code always shows dark on white, and that security keys and passkeys need HTTPS or `localhost`. Add
"Two-factor authentication" to the README's list of Account Center entries. CHANGELOG entry.
Regenerate the catalogue.

---

## US2 — Pass the second-factor step when signing in (P1)

Issue: #20. Delivers FR-002, US2's part of FR-001, FR-005, FR-008, the entrance half of SC-001,
and SC-004.

### T008 — The second-factor step

**Files**: `mvp_accounts/templates/allauth/elements/form.html`, `tests/test_elements.py`,
`tests/test_two_factor_sign_in.py`, `pyproject.toml` (`non-mirror-paths`)

Research R1, R3. `form` writes `id="{{ attrs.id }}"` when allauth gives one. Element test: a form
with an id keeps it, one without has no `id` attribute. Page tests, signing in through the password
form as a person with TOTP and recovery codes: the response lands on `mfa_authenticate`, which
renders as an entrance page with allauth's code form (acceptance 1); a correct TOTP code finishes
the sign-in; an unused recovery code on the same form finishes it too (acceptance 2); a wrong code
shows allauth's error on the page (FR-008). With WebAuthn supported, the page carries
`<form id="webauthn_form">`, the `mfa_webauthn_authenticate` button, and passes the script-hook
check. SC-004 end to end: activate through the page, sign out, sign in with a code, then with a
recovery code.

### T009 — "Trust this browser"

**Files**: `tests/test_two_factor_sign_in.py`

With `MFA_TRUST_ENABLED` (the demo's default), passing the step lands on `mfa_trust`, which renders
as an entrance page with allauth's trust and don't-trust choices (acceptance 3). Choosing either
finishes the sign-in.

### T010 — Re-authentication with a second factor

**Files**: `tests/test_two_factor_sign_in.py`

A signed-in person with TOTP whose session is not recent opens a page that asks for
re-authentication; `mfa_reauthenticate` renders as a management page with allauth's code form
(acceptance 4), a wrong code shows the error, and a correct one continues to the page asked for.

### T011 — A demo account with a second factor

**Files**: `demo/management/commands/seed_demo.py`, `tests/test_demo.py`, `README.md`, `CHANGELOG.md`

`mfa.user@example.com`, password `password`, verified primary address, an authenticator app with a
fixed secret and a set of recovery codes. Idempotent. The docstring and the closing output name the
account and say the demo's bypass code passes its second-factor step. The README names the bypass code as a demo convenience only, never a setting a host project copies. Tests: the account exists
after seeding, has both factors, and seeding twice leaves one of each; update any count of seeded
accounts. README names the account where it lists the demo's sign-ins.

---

## US3 — Use security keys and passkeys (P2)

Issue: #21. Delivers FR-005, FR-012, US3's part of FR-001, FR-007 and FR-008, and SC-002.

### T012 — The security-key list, rename and remove

**Files**: `mvp_accounts/templates/allauth/elements/table.html`, `thead.html`, `tbody.html`,
`tr.html`, `th.html`, `td.html`, `tests/factories.py`, `tests/test_elements.py`,
`tests/test_security_key_pages.py`, `pyproject.toml` (`non-mirror-paths`)

Research R2, R7. The table elements draw django-mvp's table styling; `td` keeps `align` as a class
rather than the obsolete attribute. `AuthenticatorFactory` gains a WebAuthn trait whose `data`
carries a `name` and a registration response `parse_registration_response` accepts, with
`credProps.rk` choosing passkey or security key (research R7). Page tests: with two keys,
`mfa_list_webauthn` is a management page listing both names with allauth's edit and remove links
and each key's passkey or security-key badge (acceptance 1); `mfa_edit_webauthn` renders the name
form and saving renames the key; `mfa_remove_webauthn` renders allauth's confirmation and removing
shows allauth's message.

### T013 — Adding a security key

**Files**: `tests/test_security_key_pages.py`

`mfa_add_webauthn` is a management page with the `mfa_webauthn_add` button, the passwordless
checkbox and credential input carrying their `auto_id`s, the `js_data` script, and it passes the
script-hook check (acceptance 2, SC-002).

### T014 — Passkey sign-in

**Files**: `tests/test_security_key_pages.py`

With the demo's `MFA_PASSKEY_LOGIN_ENABLED`, the sign-in page offers "Sign in with a passkey" as a
button with `id="passkey_login"` and `form="mfa_login"`, carries `<form id="mfa_login">` with the
`mfa_credential` input, and passes the script-hook check (acceptance 3). With it off (rebuild the
URLs), none of those is on the page.

### T015 — Passkey sign-up

**Files**: `tests/conftest.py`, `tests/test_security_key_pages.py`

`URLCONF_MODULES` gains `allauth.mfa.webauthn.urls` and `allauth.mfa.urls`, in that order, ahead of
`allauth.urls` (research R6); without them `mfa_signup_webauthn` never appears. Under
`MFA_PASSKEY_SIGNUP_ENABLED=True`, `ACCOUNT_EMAIL_VERIFICATION="mandatory"` and
`ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True` (rebuild the URLs; the demo leaves these off,
D5): `account_signup_by_passkey` renders as an entrance page with allauth's form; posting it and
passing email verification by code reaches `mfa_signup_webauthn`, which renders as an entrance page
with the `mfa_webauthn_signup` button and passes the script-hook check (acceptance 4).

### T016 — Re-authentication with a security key

**Files**: `tests/test_security_key_pages.py`

A signed-in person with a security key whose session is not recent: `mfa_reauthenticate_webauthn`
renders as a management page with the `mfa_webauthn_reauthenticate` button and passes the
script-hook check.

### T017 — Security keys turned off

**Files**: `tests/test_security_key_pages.py`

With `MFA_SUPPORTED_TYPES=["totp", "recovery_codes"]` (rebuild the URLs), the two-factor overview
names no security key and links to no WebAuthn page, and the second-factor step carries no
`webauthn_form` (acceptance 5, FR-007).

### T018 — Documentation

**Files**: `CONTEXT.md`, `README.md`, `CHANGELOG.md`

`CONTEXT.md` defines **Passkey** as FR-012 words it, and **Second factor** if the glossary lacks
it, with the `_Avoid_` line the file uses. README: the security-key and passkey pages, that passkey
sign-in and sign-up are the host project's settings, and that a browser only allows them over HTTPS
or on `localhost`. CHANGELOG entry.
