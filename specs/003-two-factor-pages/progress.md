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
