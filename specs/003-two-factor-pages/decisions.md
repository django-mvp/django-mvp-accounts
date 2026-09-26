# Decisions — 003 Two-factor authentication

## D1 — Reskinned elements keep allauth's ids and data attributes

allauth's security-key and passkey pages are driven by its own JavaScript, which looks up buttons,
hidden inputs, forms and its JSON configuration by id and by `data-allauth-onload`. A reskin that
drops one of those renders a page that looks right and does nothing when the button is pressed.
Keeping every id and data attribute allauth passes an element is the whole rule, and a test per page
checks the hooks are present. FS-001's field element forwards a fixed list of attributes. Where the
multi-factor pages pass one that list does not include, this feature extends the element.

## D2 — The QR code is always dark on light

Authenticator apps read QR codes as dark modules on a light background, and many cannot read an
inverted one. allauth renders the code as an image, so it keeps a light background in every theme
rather than following the page's colours.

## D3 — HTTPS for the dev server stays out of scope

Browsers only allow WebAuthn over HTTPS or on `localhost`, so security keys and passkeys cannot be
tried on the dev server's plain HTTP tailnet address. The pages and their script hooks are covered by
tests. Giving the dev server an HTTPS address is general tooling, not part of this feature.

## D4 — Passkey sign-up is specified here

`account/signup_by_passkey.html` ships in allauth's account app but only exists when the
multi-factor app is installed with passkey sign-up enabled. FS-001 left it to this feature.

## D5 — The demo leaves passkey sign-up off

allauth refuses to start with `MFA_PASSKEY_SIGNUP_ENABLED` unless email verification is mandatory
and done by code (`allauth/mfa/checks.py`, a `Critical` check). The demo keeps email verification
optional, as FS-001 set it, so turning passkey sign-up on in the demo would change how every other
sign-up in it behaves. FR-010 asks the demo to enable it so every page can be reached. The passkey
sign-up pages are instead reached in tests that turn on all three settings together, and the demo
enables every other factor. Checked against FS-001 and FS-002 before planning: neither changed
anything this spec relies on, and this is the only point where the spec and the demo's settings
meet.

**ADR:** none — a choice about the demo project, which is not distributed

## D6 — The demo accepts a fixed second-factor code

`MFA_TOTP_INSECURE_BYPASS_CODE` lets the demo's second-factor step and authenticator-app activation
be walked through without a phone. allauth raises `ImproperlyConfigured` when it is set with `DEBUG`
off, and the demo is never deployed. The suite resets it to `None`, so every test enters a real
code computed from the secret.

**ADR:** none — a choice about the demo project, which is not distributed

## D7 — "Two-factor authentication" carries no guard of its own

The entry sits in the "Account" group with `view_name="mfa_index"`, which only resolves when
`allauth.mfa` is installed. django-mvp drops an entry whose view does not resolve, which is what
the connected accounts entry already relies on, so an `apps.is_installed("allauth.mfa")` check would
repeat a test django-mvp makes.

**ADR:** docs/adr/0002-account-management-lives-in-the-account-center.md

## D8 — No page template is overridden

Every multi-factor page extends a layout FS-001 already overrides (research R1). Reskinning happens
entirely through allauth's elements, so allauth's pages keep their own markup, script tags and
JSON configuration, which is where every id its scripts look up is named.

**ADR:** docs/adr/0001-reskin-allauth-through-its-templates.md

## D9 — Design review: approved, seven findings folded into the plan

No blocking finding. The spec-level one (FR-010 and SC-001 ask for passkey sign-up in the demo,
which allauth refuses with optional email verification) stays as D5: the demo's settings are kept,
and the pages are reached in tests. The rest were edits to research.md and tasks.md: the URL
rebuild must reload allauth's multi-factor URLconfs (T015), the recovery-codes hook check runs
under show-once (T005), a test security key must be a parseable registration response (T012), the
TOTP code helper (T004), the `.bg-white` rule (T004), and repeated panel actions (R2).

**ADR:** none — local to this feature

## D10 — The security-key list needs `django.contrib.humanize`, which the demo does not install

allauth's `mfa/webauthn/authenticator_list.html` loads `{% load humanize %}`. Without
`django.contrib.humanize` in `INSTALLED_APPS` the page raises `TemplateSyntaxError`, so the demo's
security-key list returns a 500. The demo settings are outside this story's scope, so the list
tests add the app with the `settings` fixture, and the demo is reported as needing it.

**Revisit if:** the demo settings gain `django.contrib.humanize`; the fixture then goes.
