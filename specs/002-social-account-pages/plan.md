# Implementation Plan: Sign in with social accounts

**Branch**: `002-social-account-pages` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Tasks**: [tasks.md](tasks.md)

## Summary

allauth's social account pages already extend the two layouts FS-001 overrides, so they render in
the shell without new layout work (research R1). This feature adds what those layouts do not
reach: the `provider` and `provider_list` elements, drawn as django-mvp buttons carrying a
`<c-icon>` named after the provider id; the same-site redirect page, which extends nothing; and the
refusal to disconnect, which neither allauth nor FS-001's elements draw (R3). US2 adds a
"Connected accounts" entry to the Account Center's "Account" group and a card to its landing page,
both following whether allauth routes the page. The demo installs allauth's test provider and maps
its icon. No Python beyond one menu entry.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2, 6.0 and 6.1
**Primary Dependencies**: django-mvp ≥ 0.25.0 (runtime), django-allauth 65.x ≥ 65.19.4 (development only, unchanged)
**Storage**: none in the package. The demo gains allauth's social account tables
**Testing**: pytest, pytest-django, xdist. Assertions against pages rendered through allauth's real views
**Target Platform**: any Django project built on django-mvp
**Project Type**: reusable Django app (templates plus one menu module)
**Constraints**: no import of the social account app outside code that runs only when it is installed; every added string translatable
**Scale/Scope**: 2 element overrides, 2 page overrides, 1 menu entry, 1 card

## Constitution Check

| Article | How this plan meets it |
|---|---|
| I Test-first | Each element, page and entry gets a failing render test first |
| II Simplicity | Templates and one menu entry. No guard for the social account app (R4) |
| III Anti-abstraction | No tags, helpers or base classes |
| IV Integration-first | Tests drive allauth's real social account views through the test provider |
| V Security | Provider names and URLs reach the page through `{{ }}` and Cotton attributes, escaped. No flow is modified. The demo's social-only account is behind `seed_demo`'s DEBUG guard |
| VI Documentation | README social sign-in section and Account Center list, CHANGELOG, each in the story that introduces it |
| VII Dependencies | None added. The social account app ships inside django-allauth, already a development dependency |
| VIII i18n | The menu label and card text wrapped, catalogue regenerated |
| IX Data model | No models |
| X Tests | Page tests are template tests declared in `non-mirror-paths`. `menus.py` stays with `tests/test_menus.py`. One factory for allauth's `SocialAccount` |
| XIV Optional capabilities | Social account app absent: no entry, no card, no page raises (R5) |
| XV Scope | Provider configuration and icons stay the host project's (FR-006, FR-009) |

No violations.

## Design

### Package layout

```text
mvp_accounts/
├── menus.py                          # + "Connected accounts" in the Account group
├── locale/en/LC_MESSAGES/django.po   # regenerated
└── templates/
    ├── allauth/elements/
    │   ├── provider.html             # c-button with the provider id as its icon (R2)
    │   └── provider_list.html        # a wrapping row of provider buttons (R2)
    ├── socialaccount/
    │   ├── connections.html          # extends allauth's, draws the form's non-field errors (R3)
    │   └── login_redirect.html       # same-site redirect as an entrance page (R1)
    └── mvp/account/overview.html     # + Connected accounts card
```

### Demo and tests

```text
demo/
├── settings.py        # social account app, test provider, dummy icon (R6)
└── management/commands/seed_demo.py   # staff's connected account, social.user (R6)
tests/
├── settings.py                         # + GitHub provider configured in settings (R5)
├── settings_without_socialaccount.py   # allauth kept, social account app stripped
├── adapters.py                         # + a social adapter listing no providers
├── factories.py                        # + SocialAccountFactory
├── test_social_entrance_pages.py       # template tests, non-mirror
├── test_connections_page.py            # template tests, non-mirror
├── test_account_center.py              # + card
├── test_menus.py                       # + entry
└── test_without_socialaccount.py       # subprocess, non-mirror
```

### What every page test asserts

The four assertions FS-001's page tests make, unchanged: django-mvp's stylesheet is linked; the
shell's navigation is absent on entrance pages and the sidebar's navigation present on the
connections page; allauth's bare `<strong>Menu:</strong>` block is absent; and allauth's form or
text specific to that page is present. Reuse FS-001's helpers for these where the existing test
modules have them.

Every test that renders a provider button also asserts that the button's icon name equals its
provider id (SC-003). A `<c-icon>` renders through django-easy-icons, so the test reads the icon
markup the demo's mapping produces for that id, not the component tag.

### Story order

**US1 → US2, one at a time, in one working tree.** US2's connections page draws US1's provider
buttons, and both stories touch `tests/settings.py` and the demo settings. Dispatching them in
parallel would collide on those files.

## Complexity Tracking

None.
