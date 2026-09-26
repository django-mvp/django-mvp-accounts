# Progress — 003 Two-factor authentication

## 2026-09-26 · Forge · S3 plan

Did: re-read the spec against FS-001 and FS-002, delivered since it was written. No contradiction.
The one conflict found is with allauth, not a spec: passkey sign-up needs mandatory email
verification, which the demo does not use (D5). Wrote research.md, plan.md, tasks.md: 3 stories,
18 tasks, no page template overridden.
Next: design review.

## 2026-09-26T21:13:51Z · Implementer US1 · T001

Did: Installed allauth.mfa with the mfa extra in the demo (all factors except passkey sign-up, passkey login, trust, fixed bypass code); suite resets the bypass code to None; ran uv lock, uv sync, migrate.
Verified: uv run pytest tests/test_demo.py::TestDemoTwoFactor: 4 passed; entrance, social entrance and recovery page tests: 48 passed; pre-commit clean.
Next: next task.
Watch: none.

## 2026-09-26T21:14:38Z · Implementer US1 · T002

Did: Added the Two-factor authentication entry (last child of the Account group, lock icon) and a card linking to mfa_index, drawn when the page resolves.
Verified: uv run pytest tests/test_menus.py tests/test_account_center.py: 31 passed.
Next: next task.
Watch: none.

## 2026-09-26T21:15:51Z · Implementer US1 · T003

Did: Added the panel element (card, title, body, every action in the footer), the two-factor overview page tests, and AuthenticatorFactory (TOTP and recovery-code traits, built through allauth's own activation), which T004 also lists. Probed: removing panel.html fails the bare-section test.
Verified: uv run pytest tests/test_two_factor_pages.py tests/test_elements.py: 27 passed, 1 skipped (existing).
Next: next task.
Watch: none.

## 2026-09-26T21:17:08Z · Implementer US1 · T004

Did: Added the img element (escaped src/alt, bg-white with padding), the totp_code fixture in conftest, and tests for activating and deactivating the authenticator app: QR on white, dark SVG fill, stylesheet defines .bg-white, secret shown, wrong code error, correct code activates with allauth's message. The activation test commits for real because allauth adds its message on commit. AuthenticatorFactory was added in T003.
Verified: uv run pytest tests/test_two_factor_pages.py tests/test_elements.py: 38 passed, 1 skipped (existing).
Next: next task.
Watch: none.

## 2026-09-26T21:18:51Z · Implementer US1 · T005

Did: Added the textarea branch to the field element (id, readonly, rows, value slot, label kept; no whitespace around the value), the assert_script_hooks fixture in conftest, and recovery-code page tests: view page (readonly textarea id=recovery_codes, hooks under SHOW_ONCE), download, generate page and generate replaces codes with allauth's message.
Verified: uv run pytest tests/test_two_factor_pages.py tests/test_elements.py tests/test_management_pages.py tests/test_entrance_pages.py: 71 passed, 2 skipped (existing).
Next: next task.
Watch: none.

## 2026-09-26T21:19:34Z · Implementer US1 · T006

Did: Added tests/settings_without_mfa.py and a subprocess test: with allauth.mfa removed the Account Center has no two-factor entry or card, the sign-in and password pages render, nothing raises; the same script under tests.settings sees the entry, card and passkey button.
Verified: uv run pytest tests/test_without_mfa.py: 6 passed.
Next: next task.
Watch: none.

## 2026-09-26T21:19:58Z · Implementer US1 · T007

Did: README: Two-factor authentication section (which pages are reskinned once allauth.mfa is installed with the mfa extra, the package sets none of its settings, QR code always dark on white, security keys and passkeys need HTTPS or localhost) and the Account Center list; CHANGELOG entry; catalogue regenerated with makemessages -l en inside mvp_accounts/. No docs/ page describes what this story touched.
Verified: makemessages -l en: three new msgids; pre-commit run below.
Next: next task.
Watch: none.

## Implementer US1 · T002 follow-up

Did: the full-suite run found `tests/test_apps.py::TestStartup::test_entries_are_on_the_menu_after_startup` listing the Account group's children exactly. Added `two_factor` to the expected list, the minimal change; no assertion weakened.
Verified: see the full-suite run recorded in the completion report.
Next: report.
Watch: this is a pre-existing test edited outside the story's file list; named in the report's concerns.

## 2026-09-26T21:40:00Z · Implementer US2 · T008

Did: `form` element writes `id` when allauth gives one; `tests/test_two_factor_sign_in.py` covers the second-factor step (entrance page, correct code, recovery code, wrong code, security-key form id and script hooks, no security-key support) and the activate-sign out-sign in path; the new module is listed in non-mirror-paths.
Verified: `uv run pytest tests/test_two_factor_sign_in.py tests/test_elements.py::TestFormId -q` 10 passed; the id tests and the webauthn test failed first.
Next: T009.
Watch: the step tests turn MFA_TRUST_ENABLED off so a correct code finishes the sign-in; T009 covers the trust prompt.

## 2026-09-26T21:55:00Z · Implementer US2 · T009

Did: page tests for the "trust this browser" prompt: an entrance page with the trust and don't-trust choices, and either choice finishes sign-in. The suite's URL rebuild now also reloads allauth's multi-factor routes, since the prompt's route exists only when the setting is on as they are imported.
Verified: `uv run pytest tests/test_two_factor_sign_in.py -q` passed; the prompt tests errored with NoReverseMatch before the reload was added.
Next: T010.
Watch: none.

## 2026-09-26T22:00:00Z · Implementer US2 · T010

Did: page tests for re-authentication with a code. allauth's own re-authentication page asks for the password and offers the code page as an alternative; `mfa_reauthenticate` renders as a management page, shows the error on a wrong code and continues to the page asked for on a correct one.
Verified: `uv run pytest tests/test_two_factor_sign_in.py -q` 15 passed. The first version of these tests assumed the sensitive page redirects straight to `mfa_reauthenticate`; it redirects to the password page, so the tests open the code page with `?next=`.
Next: T011.
Watch: none.

## 2026-09-26T22:20:00Z · Implementer US2 · T011

Did: `seed_demo` adds mfa.user@example.com (password `password`, verified primary address, authenticator app with a fixed secret, recovery codes), built through allauth's own activation and skipped when a factor already exists; the closing output names the account and the demo's fixed code as a demo convenience. Tests for the factors, idempotence, the sign-in landing on the second-factor step and the output. README names the account and the code; CHANGELOG entry.
Verified: `uv run pytest tests/test_demo.py -q` 32 passed; new tests failed first.
Next: docs check, full verify, report.
Watch: `TestDemoSignIn::test_seeding_twice_leaves_one_verified_primary_address_each` counted four addresses and now counts five; the minimal change, named in the report.

## 2026-09-26T23:00:00Z · Implementer US3 · T012

Did: table, thead, tbody, tr, th and td elements draw django-mvp's `table` class inside a scrolling wrapper; `td` turns `align` into a `text-<align>` class. `AuthenticatorFactory` gains a `webauthn` trait (with `key_name` and `passkey`) storing a registration response built with fido2's own constructors. Page tests for the list (two keys, edit/remove links, passkey and security-key badges, empty list), rename and remove.
Verified: `uv run pytest tests/test_elements.py tests/test_security_key_pages.py -q` 40 passed, 1 skipped (a skip already in test_elements.py). Page tests failed first on the missing factory trait, then on `humanize` not being installed (D10), and the element tests failed on the bare markup.
Next: T013.
Watch: the demo's own list page needs `django.contrib.humanize` (D10).

## 2026-09-26T23:10:00Z · Implementer US3 · T013

Did: page tests for `mfa_add_webauthn`: a management page, the `mfa_webauthn_add` button, the passkey checkbox and credential input, the script-hook check, and a test that the helper catches a missing id.
Verified: `uv run pytest tests/test_security_key_pages.py::TestAddSecurityKey -q` 2 passed. The page already renders through existing elements, so the tests pass on first run; probed by removing the button element's `id` output, which failed the test, then restored.
Next: T014.
Watch: none.

## 2026-09-26T23:15:00Z · Implementer US3 · T014

Did: page tests for passkey sign-in: an entrance page with the `passkey_login` button linked to `mfa_login`, the `mfa_login` form with its credential input, the script-hook check; with passkey sign-in off (URLs rebuilt) none of them is on the page.
Verified: `uv run pytest tests/test_security_key_pages.py::TestPasskeySignIn -q` 2 passed. Existing elements already carry the ids, so the tests passed on first run; probed by removing the button element's `form` output, which failed, then restored.
Next: T015.
Watch: none.

## 2026-09-26T23:30:00Z · Implementer US3 · T015

Did: `allauth.mfa.webauthn.urls` added to the URL rebuild list, ahead of `allauth.mfa.urls`. Tests for passkey sign-up under passkey sign-up + mandatory verification + verification by code: `account_signup_by_passkey` is an entrance page; posting an address and the emailed code reaches `mfa_signup_webauthn`, an entrance page with the `mfa_webauthn_signup` button and the script-hook check.
Verified: `uv run pytest tests/test_security_key_pages.py -q` 14 passed. Without the conftest line the whole file fails (`mfa_signup_webauthn` not found) once an earlier test has imported the webauthn URLs with sign-up off; run alone the class passes either way.
Next: T016.
Watch: the verification-code page is `account_email_verification_sent`, not `account_confirm_email`.

## 2026-09-26T23:40:00Z · Implementer US3 · T016

Did: page test for `mfa_reauthenticate_webauthn` with a stored security key and a session that has no recent sign-in: a management page with the `mfa_webauthn_reauthenticate` button and the script-hook check.
Verified: `uv run pytest tests/test_security_key_pages.py::TestReauthenticateWithSecurityKey -q` 1 passed; passed on first run since the page already renders through existing elements, and failed when the button element's `id` output was removed (restored afterwards).
Next: T017.
Watch: none.

## 2026-09-26T23:50:00Z · Implementer US3 · T017

Did: tests with `MFA_SUPPORTED_TYPES=["totp", "recovery_codes"]` (URLs rebuilt): the overview names no security key or passkey and links to no security-key page; the second-factor step, for a person who has a stored key, shows only the code form, with no `webauthn_form` or security-key button.
Verified: `uv run pytest tests/test_security_key_pages.py::TestSecurityKeysTurnedOff -q` 2 passed; both failed with `webauthn` added back to the supported types, then restored.
Next: T018.
Watch: none.

## 2026-09-26T23:55:00Z · Implementer US3 · T018

Did: CONTEXT.md defines Second factor and Passkey; README covers the security-key pages, passkey sign-in and sign-up as the host project's settings (with the email-verification requirement), the `django.contrib.humanize` requirement and HTTPS/localhost; CHANGELOG entry.
Verified: documentation only, no test covers it; `uv run pre-commit run --all-files` clean, checked by reading the three files against the settings named.
Next: full verify, report.
Watch: the demo does not install `django.contrib.humanize`, so its security-key list page fails to render (D10); reported in concerns.

## 2026-09-26 · Forge · S5 converge

Did: every FR and SC traced to a delivered task; no migrations in the package. The demo installs
`django.contrib.humanize`, which allauth's security-key list loads, and the suite's fixture adding it
is gone (D10). The cell element's alignment used a class django-mvp's stylesheet does not ship, so
it now uses `text-end`, and the test pinning the class was removed. D1 graduated to ADR 0004. Every
decision carries its ADR verdict. Patch coverage of the package's Python: 100%.
Next: code review.
