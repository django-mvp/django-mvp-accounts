# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
  Everything not yet released goes under [Unreleased], grouped by change type:
  Added, Changed, Deprecated, Removed, Fixed, Security. Prepare Release promotes
  that section to a version heading and dates it.

  Do NOT write a version heading by hand. Tag Release fires on any push to main
  that touches pyproject.toml, and the only thing stopping it cutting a release
  from that push is the absence of a `## [X.Y.Z]` section matching the version
  in pyproject.toml. Writing one here defeats that guard, and the repository
  ends up with a tag and a GitHub Release for a version nobody prepared.

  Write for someone deciding whether to upgrade. Say what changed for them and
  what they have to do about it, not which files moved.
-->

## [Unreleased]

### Added

- The package, generated and not yet doing anything.
- Django 6.1 is supported, and tested on every change alongside 5.2 and 6.0.
- django-allauth's sign-in, sign-up, sign-out, sign-in-by-code and account-inactive pages, and its
  "sign-up closed" page, now render as django-mvp entrance pages: no sidebar, one centred card, with
  messages shown above it. allauth's forms, buttons, alerts and headings are drawn from django-mvp's
  components. To use them, list `mvp_accounts` in `INSTALLED_APPS` ahead of `allauth` and `mvp`, and
  include `allauth.urls` and `mvp.urls`. django-allauth 65.19.4 up to, but not including, 66 is
  supported. A template of your own with the same name as one of allauth's still takes precedence.

### Changed

- The minimum django-mvp version is 0.25.0.
- The package is built with hatchling instead of poetry-core, and developed with uv instead of
  Poetry.
