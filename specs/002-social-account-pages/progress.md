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
