# Decisions — 001 Accounts, sign-in and recovery on the site's own pages

## allauth is a development dependency only

The package reskins allauth by putting templates where allauth's template lookup finds them. Those
templates are only ever loaded by allauth's own views, so a project without allauth never touches
them, and a project with allauth gets them without the package doing anything at runtime. Declaring
allauth as a runtime dependency would add nothing the host project does not already have when it
wants these pages, and would force it on projects that do not.

The constitution (Article XIII) asks for every upstream dependency to be bounded to the major versions
CI runs. With allauth in the development group only, that bound applies to what CI installs and
cannot reach a host project. The README therefore states the supported range, and the bound in the
development group keeps CI on it.

## No configuration checks

The package does not check allauth's middleware, authentication backends, settings or URL
configuration. Setting allauth up is the host project's job, and allauth documents it. The only
adoption step this package adds, listing it ahead of `allauth` in `INSTALLED_APPS`, is documented
rather than checked.

## Sign-up by passkey belongs to two-factor authentication

`account/signup_by_passkey.html` ships in allauth's account app, but the page only exists when
allauth's multi-factor app is installed and passkey sign-up is enabled. It is reskinned and tested
with the rest of the multi-factor pages in #7.

## Glossary correction

`CONTEXT.md` says closing an account is something the authentication package provides. allauth has
no account deletion. The implementation corrects the entry (FR-013), and account deletion stays out
of this feature. It is either a request to allauth or a data-rights concern for django-mvp-compliance.
