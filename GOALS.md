# Goals

These are the standing directions `django-mvp-accounts` works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
package is, what it stays out of, and the principles that settle a close call, read the
*Scope & philosophy* section of the [README](README.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.
- **Aspirational** — a genuine want whose absence never makes the package incomplete.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | At least one popular Django authentication package is integrated, so a person can sign up, sign in, recover access and manage their account through it | Essential | | |
| G2 | Every entrance and account page looks like part of the host project: its shell, its theme and its menus | Essential | | |
| G3 | Adopting it is as simple as possible, and which pages and menu entries appear depends on what the project has installed | Essential | | |
| G4 | When the project has a REST API, a person can create, see and revoke their own API tokens | Expected | | |
| G5 | The latest release of every integrated package is supported wherever possible | Expected | | |

_Written 2026-09-24. Revise as the goals change._
