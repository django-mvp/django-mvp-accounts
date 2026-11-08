# ADR 0007 — Organisations come from django-organizations

**Status:** accepted, not yet implemented

## Decision

Organisations are part of this package, built on
[django-organizations](https://github.com/bennylope/django-organizations).

- django-organizations keeps organisations, their members, their invitations and each member's
  owner, admin or member role. This package adds no organisation model or migration of its own,
  and subclasses none of django-organizations' models.
- This package provides the pages for them in the Account Center: creating an organisation,
  inviting people and accepting an invitation, the members page, and switching between the
  organisations a person belongs to.
- The pages live in a subpackage, `mvp_accounts/organizations/`, installed with an
  `organizations` extra, the same way the API tokens pages sit behind the `api` extra
  ([ADR 0005](0005-the-package-provides-the-api-tokens-pages.md)). A project that has not
  installed django-organizations gets no entry, no card and no import error.
- A role says who runs an organisation and nothing more. What a member may do with the host
  project's objects is the host project's to decide, with whatever permissions package it uses.
- Paying for an organisation's places is django-mvp-payments'. This package never depends on a
  payment provider.

## Why

Managing the organisations you belong to is another way of managing your account, and it is
reached from the same place. This package is still light, so it can take organisations without
crowding what is already here, and adding them here means one package fewer to maintain than a
package of their own would.

django-organizations is the established package for this (about 1,400 GitHub stars and 83,000
downloads a month in November 2026) and includes invitations, so there is nothing to build that it
already has. django-invitations, the usual alternative for invitations, is GPL.

Keeping billing out keeps this package free of any payment provider. A project that groups people
without charging them installs organisations and nothing else.

## Revisit if

Organisations grow pages that are not about a person's own membership, such as an organisation's
public profile or its own settings. Those would no longer be account management, and would be a
reason for a package of their own.
