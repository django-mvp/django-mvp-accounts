# Brainstorm

Working notes from founding the package. These are conclusions reached before
any code existed, not ratified decisions. Anything here that hardens goes to
`CONSTITUTION.md` or a decision record under `docs/adr/`.

## What already exists

Checked on 2026-09-24.

| Package | Latest | Released | What it covers |
|---|---|---|---|
| [django-allauth](https://pypi.org/project/django-allauth/) | 65.19.4 | 2026-09-17 | Accounts, sign-in, email verification, social login, two-factor authentication, user sessions. Actively maintained, MIT |
| [Django REST framework](https://pypi.org/project/djangorestframework/) | 3.18.1 | 2026-09-07 | The API layer, including a built-in token model limited to one token per user. BSD-3 |
| [django-rest-knox](https://pypi.org/project/django-rest-knox/) | 5.1.0 | 2026-07-12 | Tokens for Django REST framework with several per user, expiry, and tokens stored hashed. Jazzband, MIT |
| [djangorestframework-api-key](https://pypi.org/project/djangorestframework-api-key/) | 3.1.0 | 2025-04-04 | Keys for machine clients rather than people. Last release over a year ago |
| [dj-rest-auth](https://pypi.org/project/dj-rest-auth/) | 7.2.0 | 2026-03-15 | Sign-in and sign-up *as an API*, for single-page and mobile clients |
| [drf-auth-kit](https://pypi.org/project/drf-auth-kit/) | 1.8.1 | 2026-08-10 | The same job as dj-rest-auth, with JWT cookies and typed schemas |
| [django-accounts-center](https://github.com/django-mvp/django-accounts-center) | 0.7.1 | — | The predecessor: allauth's pages rendered in django-mvp's shell, through a plugin system of sub-apps |

## Conclusions

**Every building block exists and is healthy, and none of them renders into
django-mvp.** That gap is the whole reason for this package. It should never
grow its own account model, sign-in flow or token format. Each of those has a
maintained, widely used implementation above.

**dj-rest-auth and drf-auth-kit solve a different problem.** They expose
sign-in *over* an API for clients that have no server-rendered pages. This
package is for a person using the site who wants a token to reach its API.
Neither is a dependency, and neither is a competitor.

**Which token package is still open.** Django REST framework's own token model
allows one token per user, cannot expire, and stores the token in plain text.
django-rest-knox fixes all three. That points at knox, but the choice belongs
to the specification for API tokens, not to founding notes.

**django-accounts-center is superseded, not extended.** Its plugin system for
third-party sub-apps is more machinery than the job needs. The replacement
starts from the pages people use and adds structure only where a second real
use appears.
