# Implementation Plan: Two-factor authentication

**Branch**: `003-two-factor-pages` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

Every page allauth's multi-factor app renders already extends one of the two layouts FS-001
overrides, and re-authentication already picks the management layout (research R1). So this
feature overrides no page template. It adds the elements those pages use and FS-001 never needed:
`panel` for the two-factor overview, `img` for the QR code, and the table elements for the
security-key list (R2). It extends two of FS-001's elements so they keep what allauth's scripts
look up: `form` keeps its `id`, and `field` draws the recovery codes' read-only text area (R3). The
QR code sits on a fixed white background in every theme (R4). A "Two-factor authentication" entry
joins the Account Center's "Account" group and a card joins its landing page, both following
whether allauth routes its two-factor page. The demo installs the multi-factor app with every
factor turned on except passkey sign-up, which allauth only allows with mandatory email
verification (R5, decisions.md D5).

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2, 6.0 and 6.1
**Primary Dependencies**: django-mvp ≥ 0.25.0 (runtime, unchanged), django-allauth 65.x ≥ 65.19.4 with its `mfa` extra (development only)
**Storage**: none in the package. The demo gains allauth's `Authenticator` table
**Testing**: pytest, pytest-django, xdist. Assertions against pages rendered through allauth's real views
**Target Platform**: any Django project built on django-mvp
**Project Type**: reusable Django app (templates plus one menu module)
**Constraints**: nothing imports `allauth.mfa` outside code that runs only when it is installed; every added string translatable
**Scale/Scope**: 8 new element overrides (`panel`, `img`, six table elements), 2 extended (`form`, `field`), 1 menu entry, 1 card, 0 page templates

## Constitution Check

| Article | How this plan meets it |
|---|---|
| I Test-first | Each element, entry and page gets a failing render test first |
| II Simplicity | Templates and one menu entry. No guard on `allauth.mfa` in `menus.py`: an entry whose view does not resolve is dropped by django-mvp, as the connections entry already relies on |
| III Anti-abstraction | No tags, helpers or base classes in the package. One test helper checks script hooks for every page (R3) |
| IV Integration-first | Tests drive allauth's real multi-factor views with real TOTP codes and recovery codes |
| V Security | No flow is modified. Values reach the page through `{{ }}` and Cotton attributes, escaped. The TOTP bypass code is demo-only, refused by allauth without `DEBUG`, and reset to `None` in the suite (D6) |
| VI Documentation | README two-factor section, CHANGELOG and `CONTEXT.md` passkey term, each in the story that introduces it |
| VII Dependencies | None at runtime. The development group takes allauth's `mfa` extra (`qrcode`, `fido2`) |
| VIII i18n | Menu label and card text wrapped, catalogue regenerated |
| IX Data model | No models |
| X Tests | Page tests are template tests declared in `non-mirror-paths`. `menus.py` stays with `tests/test_menus.py`. One factory per allauth model touched (`Authenticator`, by type) |
| XIV Optional capabilities | Multi-factor app absent: no entry, no card, no page raises (T006) |
| XV Scope | Which factors are enabled and WebAuthn options stay the host project's (FR-009) |

No violations.

## Design

### Package layout

```text
mvp_accounts/
├── menus.py                          # + "Two-factor authentication" in the Account group
├── locale/en/LC_MESSAGES/django.po   # regenerated
└── templates/
    ├── allauth/elements/
    │   ├── panel.html                # c-card: title, body, every action (R2)
    │   ├── img.html                  # QR on bg-white with padding (R4)
    │   ├── table.html, thead.html, tbody.html, tr.html, th.html, td.html   # DaisyUI table (R2)
    │   ├── form.html                 # + id (R3)
    │   └── field.html                # + textarea / readonly / rows / value slot (R3)
    └── mvp/account/overview.html     # + Two-factor authentication card
```

### Menu entry

A `MenuItem` named `two_factor`, `view_name="mfa_index"`, label "Two-factor authentication", icon
`lock`, appended as the last child of the existing "Account" `MenuGroup` in `menus.py`. Never
top-level, never a `MenuCollapse`. No `apps.is_installed("allauth.mfa")` guard: without the app
`mfa_index` does not resolve and django-mvp drops the entry, the same way it drops the connected
accounts entry without the social account app. The module docstring's list of such entries gains
this one.

### Demo and tests

```text
demo/
├── settings.py                 # allauth.mfa, supported types, passkey sign-in, trust, bypass code (R5)
└── management/commands/seed_demo.py   # mfa.user@example.com with an authenticator app and recovery codes
tests/
├── settings.py                 # MFA_TOTP_INSECURE_BYPASS_CODE = None
├── settings_without_mfa.py     # allauth kept, allauth.mfa stripped
├── factories.py                # + AuthenticatorFactory (TOTP, recovery codes, WebAuthn traits)
├── conftest.py                 # + script-hook helper (R3)
├── test_two_factor_pages.py    # management pages, non-mirror
├── test_two_factor_sign_in.py  # entrance pages and re-authentication, non-mirror
├── test_security_key_pages.py  # WebAuthn and passkey pages, non-mirror
├── test_account_center.py      # + card
├── test_menus.py               # + entry
├── test_elements.py            # + panel, img, table, form id, field textarea
└── test_without_mfa.py         # subprocess, non-mirror
```

### What every page test asserts

FS-001's four assertions, reusing its helpers: django-mvp's stylesheet is linked; the shell's
navigation is absent on entrance pages and the sidebar's navigation present on management pages;
allauth's bare `<strong>Menu:</strong>` block is absent; and the form or text that page exists for
is present. A multi-factor page additionally asserts it is not allauth's bare `panel` or `table`
markup, where it uses one.

Every page that loads an allauth script (`data-allauth-onload`) also runs the script-hook check
(R3): each id the script's JSON names is the `id` of an element on the page. This is SC-002, and it
fails if any element drops its id.

No test pins button width, stacking, spacing or variant. The QR code's white background is the one
styling a test holds, because the spec makes it a contract (FR-006).

### Story order

**US1 → US2 → US3, one at a time, in one working tree.** All three touch the demo and suite
settings, `tests/factories.py` and the element overrides. US2's sign-in step needs the authenticator
app US1 sets up, and US3's security-key panel on the overview is drawn by US1's `panel`.

## Complexity Tracking

None.
