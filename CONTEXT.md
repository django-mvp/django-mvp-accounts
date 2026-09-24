# django-mvp-accounts

Domain vocabulary for django-mvp-accounts: sign-up, sign-in, account
management and API access for django-mvp projects, assembled from third-party
packages.

The terms below are the ones to use in issues, commits and tests. Several exist
because allauth, Django and Django REST framework each use the same English
words for different things.

## Core concepts

**Host project**:
The Django project that installs this package. It owns the theme, the base
template, the user model and the URLs. This package renders into it and decides
none of those.
_Avoid_: consumer, client, downstream.

**Account**:
A person's identity on the host project — the user record, the email addresses
attached to it, and the ways they can prove it is theirs. Creating, changing and
closing an account is what the authentication package provides and this
package presents.
_Avoid_: profile (the host project's own data about a person, which this
package does not own), user (fine in code, where it means the Django model, but
not as a synonym for the whole account).

**Authentication package**:
The third-party Django package that provides accounts, sign-in and recovery.
This package is not tied to one, but django-allauth is the only one supported
so far. Behaviour specific to it is named as allauth's, never presented as how
accounts work in general.
_Avoid_: backend (Django's authentication backends are a different thing),
provider (allauth's word for a social login service such as GitHub).

**Sign-in**:
Proving who you are to the site in a browser, ending in a session. Covers
password, social and passwordless sign-in, and a second factor where one is set
up.
_Avoid_: login and log in (allauth's URL names use them, the prose here does
not), authentication as a synonym (it also covers API tokens).

**Access**:
Being able to reach your own account, through a browser session or an API
token. The whole package is about access in this sense.
_Avoid_: using it to mean what a signed-in person is allowed to do. That is
authorisation, which this package does not handle (see below).

**API token**:
A secret a person creates for themselves to reach the host project's API
without a browser. They can create several, see when each was last used, and
revoke any of them. Only exists when the host project has installed Django REST
framework.
_Avoid_: API key (a key usually identifies a program rather than a person),
access token (OAuth's term, for a token issued to a third-party application),
password.

**Account management**:
The pages a signed-in person uses to change their own account: email
addresses, password, second factor, connected social accounts, active
sessions, and API tokens.
_Avoid_: settings (Django settings), dashboard, admin (Django's admin site,
which is for staff managing other people's accounts).

**Entrance**:
The pages someone sees before they are signed in: sign-in, sign-up, password
reset and email verification. They render outside the application shell's
navigation, because a person who is not signed in has nowhere to navigate to.
_Avoid_: auth pages, login screens.

## Terms deliberately not used

**Access control, permissions, roles, groups**: authorisation, meaning who may
do what. Out of scope. They belong to the host project.

**Integration**, for a supported third-party package: it was the name of
django-accounts-center's plugin system, which this package does not carry
forward. Name the package instead: "the allauth pages", "API tokens".
