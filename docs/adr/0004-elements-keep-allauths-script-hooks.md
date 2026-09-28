# ADR 0004 — Reskinned elements keep the ids allauth's scripts look up

**Status:** accepted

## Decision

Every `allauth/elements/*.html` override writes out each `id` allauth passes the element, and
every `form=` target, unchanged. The ids allauth's scripts use are named in JSON that allauth's own
page templates write (`<script data-allauth-onload="…">`), so the package overrides no template
that carries a script.

The suite checks this per page. For every `data-allauth-onload` script on a rendered page, each id
its JSON names must be the `id` of an element on that page (`assert_script_hooks` in
`tests/conftest.py`). Every page allauth's JavaScript drives runs the check: adding a security key,
passkey sign-in and sign-up, the second-factor step, re-authentication with a key, and recovery
codes.

## Why

The security-key, passkey and recovery-code pages do their work in allauth's JavaScript, which
finds its buttons, hidden inputs and forms with `getElementById`. An element that draws the right
component but drops the id produces a page that looks finished and does nothing when the button is
pressed. No server-side test sees that, and the browser only reports it at the moment a person
tries to add a key. Reading the ids from the page's own script configuration means the check follows
whatever allauth names in a later release, without a list kept by hand.

## Revisit if

allauth stops configuring its scripts through `data-allauth-onload` JSON, or starts finding
elements by something other than their id.
