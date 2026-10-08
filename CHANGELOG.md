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

## [v0.2.0] - 2026-10-08

### Added

- API tokens pages for projects that use [django-rest-knox](https://github.com/jazzband/django-rest-knox):
  a list of a person's tokens, a page to create one and a page to revoke one, drawn in the
  Account Center, with an "API tokens" entry in its menu and a card on its landing page. They
  appear only when the project installs the new `api` extra, adds `knox` to `INSTALLED_APPS` and
  includes `mvp_accounts.tokens.urls`; a project without django-rest-knox or Django REST
  framework gets nothing and is otherwise unchanged. A person creates a token by choosing how
  long it lasts (7 days, 30 days, 90 days, 1 year or never) and sees its complete value once,
  on the tokens page; the package stores nothing but what knox keeps. Revoking a token asks
  first and takes effect at once; changing a password does not revoke tokens. The pages honour knox's
  `TOKEN_LIMIT_PER_USER`, which knox leaves unset, so a project should set one. Every
  signed-in person may use the pages, unless the project sets `MVP_ACCOUNTS_API_TOKEN_ACCESS` to
  a function that says who may: a person it turns away gets a 403 from the pages and sees no
  entry or card, though tokens they already hold keep working. See "API tokens" in the README.
- The "Account" heading is now drawn in a project without django-allauth too, when the API tokens
  pages are routed.

### Changed

- **Breaking: django-mvp 0.27.0 is now the minimum.** That release draws forms with
  django-mvp-forms in place of crispy-tailwind and takes its basic components from
  daisy-cotton, so a project upgrading this package follows django-mvp's own upgrade notes
  for [0.26.0](https://github.com/django-mvp/django-mvp/releases/tag/v0.26.0) and
  [0.27.0](https://github.com/django-mvp/django-mvp/releases/tag/v0.27.0): add
  `"daisy_cotton"` directly below `"mvp"` in `INSTALLED_APPS`, replace `"crispy_tailwind"`
  with `"mvp_forms"`, and set `CRISPY_TEMPLATE_PACK` and `CRISPY_ALLOWED_TEMPLATE_PACKS` to
  `daisyui`. Nothing else is needed for this package's pages.
- A field drawn on its own, such as the new address on the email page or the phone number
  on the phone page, is a `<fieldset id="<id>-field">` holding a `<label>` and the control.
  A radio or checkbox sits inside its label.

### Fixed

- A field drawn on its own now points at its help text and its errors through
  `aria-describedby`, so a screen reader announces them with the field. The help text has
  the id `<id>-field-description` and the errors `<id>-field-errors`.

## [v0.1.0] - 2026-09-29

### Added

- The package, generated and not yet doing anything.
- Django 6.1 is supported, and tested on every change alongside 5.2 and 6.0.
- django-allauth's sign-in, sign-up, sign-out, sign-in-by-code and account-inactive pages, and its
  "sign-up closed" page, now render as django-mvp entrance pages: no sidebar, one centred card, with
  messages shown above it. allauth's forms, buttons, alerts and headings are drawn from django-mvp's
  components. To use them, list `mvp_accounts` in `INSTALLED_APPS` ahead of `allauth` and `mvp`, and
  include `allauth.urls` and `mvp.urls`. django-allauth 65.19.4 up to, but not including, 66 is
  supported. A template of your own with the same name as one of allauth's still takes precedence.
- allauth's password reset pages (by link and by code) and its email verification pages (by link and
  by code, including "verified email required") render as entrance pages too.
- With allauth installed, django-mvp's Account Center gains Email, Password and Phone number menu
  entries and a card for each page on its landing page. Phone number appears only when phone
  numbers are on. Without allauth the package adds nothing. An English translation catalogue is
  included.
- allauth's account management pages (email, change email, password change and set, phone change
  and phone verification, re-authentication) render in django-mvp's Account Center, inside the
  shell with its sidebar and messages. Pages allauth builds on its entrance base render as
  management pages for a signed-in person, so phone verification after a change is one, and the
  same page during sign-up stays an entrance page. Until django-mvp#358 ships, these pages do not
  get the Account Center's container padding.
- allauth's social sign-in pages (confirm, extra sign-up step, cancelled, failed, and the same-site
  redirect page) render as django-mvp entrance pages. The sign-in and sign-up pages show one button
  for each provider allauth lists, drawn from django-mvp's button with the provider's name. Each
  button's icon is named after allauth's provider id, so your django-easy-icons setup needs an icon
  under each id of a provider you configure. With `DEBUG` off a missing icon raises, as
  `EASY_ICONS_FAIL_SILENTLY` defaults to `DEBUG`. The package ships no provider icons. The demo
  installs allauth's test provider.
- With allauth's social account app installed, django-mvp's Account Center gains a Connected
  accounts menu entry, in the "Account" group after Phone number, and a card on its landing page.
  The connections page renders in the Account Center, and shows allauth's errors above its
  markup, including its refusal to disconnect the only way a person can sign in. Without the
  social account app the entry and card do not appear. The demo seeds an account with a connected
  test provider account and one with no password.
- With allauth's multi-factor app (`allauth.mfa`, from `django-allauth[mfa]`) installed,
  django-mvp's Account Center gains a Two-factor authentication menu entry, after Connected accounts
  in the "Account" group, and a card on its landing page. The two-factor overview, activating and deactivating the
  authenticator app, and the recovery codes pages (view, download, generate) render in the
  Account Center. The overview draws each factor as a card with all of its actions. The QR code is
  always dark on white, in every theme, and the recovery codes are shown in a read-only text
  area. Which factors are enabled stays your choice through allauth's `MFA_*` settings. Without
  the multi-factor app the entry and card do not appear. The demo installs it with the
  authenticator app, recovery codes, security keys, passkey sign-in and trusted browsers turned
  on, and accepts a fixed code (`123456`) for the authenticator app while `DEBUG` is on.
- The second-factor step of signing in, the "trust this browser" prompt and re-authentication with a
  code render as django-mvp pages: the first two as entrance pages, the last in the Account Center.
  The form element keeps the `id` allauth gives it, which the security-key button on the sign-in
  step needs to find its form. The demo seeds `mfa.user@example.com`, with the password `password`,
  an authenticator app and recovery codes; the demo's fixed code passes its second-factor step.
- With `"webauthn"` in `MFA_SUPPORTED_TYPES`, allauth's security-key pages render as django-mvp
  pages: the list, adding, renaming and removing a key, and re-authenticating with one in the
  Account Center. With `MFA_PASSKEY_LOGIN_ENABLED` the sign-in page offers "Sign in with a
  passkey", and with `MFA_PASSKEY_SIGNUP_ENABLED` the two passkey sign-up pages are entrance
  pages. allauth's tables are drawn with django-mvp's table class. Every page keeps the ids and
  data attributes allauth's JavaScript looks for. The security-key list needs
  `django.contrib.humanize` in `INSTALLED_APPS`. Browsers only allow security keys and passkeys
  over HTTPS or on `localhost`. The demo leaves passkey sign-up off, because allauth requires
  mandatory email verification by code for it, among other settings.
- With allauth's user sessions app installed, django-mvp's Account Center gains a Sessions menu
  entry, in the "Account" group after Two-factor authentication, and a card on its landing page. allauth's
  sessions page renders in the Account Center and lists each browser a person is signed in from,
  with its address, browser and the "Current" marker, and a "Last seen at" column when
  `USERSESSIONS_TRACK_ACTIVITY` is on. The page's button signs out every other session without
  asking first, and the confirmation appears in the shell. With one session the button is "Sign
  Out" and uses the site's own sign-out. The table scrolls sideways inside its own area on a narrow
  screen. To use it, install `allauth.usersessions`, its middleware and `django.contrib.humanize`.
  Without the app the entry and card do not appear. The demo signs `regular.user@example.com` in
  from two more browsers.

### Changed

- The minimum django-mvp version is 0.25.0.
- The package is built with hatchling instead of poetry-core, and developed with uv instead of
  Poetry.
