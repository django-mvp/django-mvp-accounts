# Progress — 002 Sign in with social accounts

## 2026-09-26 · Forge · S3 plan

Did: re-read the spec against FS-001 (no contradiction); plan.md, research.md, tasks.md; ledger at
PLAN. Next: design review, then US1.

## 2026-09-26T19:57:09+02:00 · Implementer US1 · T001

Did: social account app and test provider in the demo (dummy icon mapped); GitHub app configured in the suite's settings.
Verified: `uv run pytest tests/test_demo.py::TestDemoSocialAccounts` 2 passed (red first: NoReverseMatch); test_without_allauth 4 passed; pre-commit clean; migrate run.
Next: T002
Watch: -

## 2026-09-26T19:58:02+02:00 · Implementer US1 · T002

Did: provider and provider_list elements (c-button with the provider id as icon, name as text and title, in a wrapping row); NoProvidersSocialAdapter; tests/test_social_entrance_pages.py (TestProviderButtons) added to non-mirror-paths.
Verified: `uv run pytest tests/test_social_entrance_pages.py` red first (icon, shell-button assertions failed on allauth's bare list), then 13 passed; pre-commit clean.
Next: T003
Watch: -

## 2026-09-26T19:58:37+02:00 · Implementer US1 · T003

Did: TestSocialEntrancePages: confirmation page, test provider's form, extra sign-up step with a field error, cancelled page (via redirect), failed page (by URL), completed sign-in.
Verified: `uv run pytest tests/test_social_entrance_pages.py` 20 passed. These pages already render through FS-001's layouts, so the tests passed on first run; probed by removing allauth/layouts/entrance.html: 8 failed, then restored.
Next: T004
Watch: allauth answers the failed page with 401, so that test makes the shared assertions inline (the helper wants 200).

## 2026-09-26T19:58:56+02:00 · Implementer US1 · T004

Did: socialaccount/login_redirect.html extending socialaccount/base_entrance.html (title, refresh in extra_head, Continue link through the p element); TestSameSiteRedirectPage.
Verified: red first (bare document, no stylesheet); `uv run pytest tests/test_social_entrance_pages.py` 21 passed.
Next: T005
Watch: -

## 2026-09-26T19:59:15+02:00 · Implementer US1 · T005

Did: README section "Signing in with other accounts" and a CHANGELOG Added entry. Nothing under docs/ describes the touched surface (ROADMAP, adr, agents, brainstorm only).
Verified: pre-commit clean; wording checked against the brief's acceptance list.
Next: full verify, report.
Watch: -

## 2026-09-26T20:05:28+02:00 · Implementer US2 · T006

Did: MenuItem for socialaccount_connections after Phone number in the Account group; docstring updated.
Verified: uv run pytest tests/test_menus.py: 16 passed. Red first (entry absent).
Next: Icon name `link` draws bi-link-45deg in django-mvp's pack.
Watch: tests/test_apps.py still asserts exactly email, password, phone.

## 2026-09-26T20:05:28+02:00 · Implementer US2 · T007

Did: Connected accounts card after the phone card, drawn when the URL resolves.
Verified: uv run pytest tests/test_account_center.py: 11 passed. Red first.
Next: T008
Watch: -

## 2026-09-26T20:05:28+02:00 · Implementer US2 · T008

Did: SocialAccountFactory; socialaccount/connections.html adds an error alert via block.super; tests/test_connections_page.py (9 tests).
Verified: uv run pytest tests/test_connections_page.py: 9 passed. Refusal and required-field tests red before the template.
Next: T009
Watch: allauth's disconnect message reads 'The third-party account has been disconnected.'

## 2026-09-26T20:05:28+02:00 · Implementer US2 · T009

Did: Settings without allauth.socialaccount; runner lifted into the run_in_subprocess fixture in tests/conftest.py, test_without_allauth.py assertions untouched.
Verified: uv run pytest tests/test_without_socialaccount.py tests/test_without_allauth.py: 11 passed; pointing the new module at tests.settings fails 3 tests, so it is not vacuous.
Next: T010
Watch: -

## 2026-09-26T20:05:28+02:00 · Implementer US2 · T010

Did: seed_demo: staff uid 1001, social.user with unusable password and uid 2002, idempotent, closing output names both; catalogue regenerated; README and CHANGELOG updated; seed_demo run against the demo database.
Verified: uv run pytest tests/test_demo.py::TestSeededSocialAccounts: 4 passed. Full suite: 2 failed (see decisions.md).
Next: Report.
Watch: A fourth verified primary address breaks the existing count of three in test_demo.py.

## 2026-09-26 · Forge · S5 converge

Did: every FR and SC traced to a delivered task; no migrations on the branch; the provider-icon
decision graduated to ADR 0003; every decision carries its ADR verdict. Next: code review.
