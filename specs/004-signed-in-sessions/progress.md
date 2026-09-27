# Progress — 004 Signed-in sessions

## 2026-09-27 · Forge · S3 plan

Did: re-read the spec against FS-002 (no contradiction, D4); plan.md, research.md, tasks.md;
ledger at PLAN. Next: design review, then US1.

## 2026-09-27 · Forge · S3R design review

Did: one reviewer, three lenses, approve; four findings applied to research R5 and T005, T007, T009,
T011 (D9). Next: US1.

## 2026-09-27 · Implementer US1 · T001–T008

Did: demo installs the user sessions app, humanize, middleware and tracking (T001); six table elements
copied byte-for-byte, verified with diff (T002); Sessions entry after Connected accounts (T003) and
card (T004); sessions page tests and `UserSessionFactory` (T005); subprocess test without the app
(T006); two seeded sessions for regular.user (T007); README, CONTEXT, CHANGELOG, en catalogue (T008).
Verified: each task's narrow class red then green; full suite `uv run pytest -n auto --dist loadscope`
180 passed, 2 skipped, 1 failed (`tests/test_apps.py::TestStartup::test_entries_are_on_the_menu_after_startup`,
which pins the Account group's children to four names; the new entry makes it five). Lint, mypy,
deptry and build clean.
Next: Forge decides how the pre-existing test in `tests/test_apps.py` is updated; it is outside this story's files.
Watch: SC-001 probe (manage layout removed) failed one page test, then restored; not committed.
