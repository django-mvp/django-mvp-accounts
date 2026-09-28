# django-mvp-accounts Constitution

The standards every change to this repository is held to. Read it before
planning a change and again when reviewing one.

This is the slow-moving document. It is amended deliberately, never in the
middle of the work it would affect, and an amendment updates the version and
the date in the footer. If a rule here is wrong, change the rule in its own
pull request and then do the work.

**Articles I to X are the general standard and are the same in every package
built this way.** Articles XI onward are this package's own, and are the ones
to write. Everything below the articles — the quality bar and the
non-negotiables — applies as written.

## Core articles

### Article I — Testing

Every change follows
[`docs/contributing/standards/testing.md`](docs/contributing/standards/testing.md):
what gets a test and what does not, the test-first cycle, test structure and
fixtures, and the coverage floors.

### Article II — Simplicity

Start with the simplest design that satisfies the requirement. A new
dependency, a new abstraction, or a new piece of infrastructure each need a
stated justification recorded with the change. Build what is needed now, not
what might be needed.

### Article III — Anti-Abstraction

No wrapper layers, base classes, or future-proofing indirection without a
present, concrete second use. Duplication is cheaper than the wrong
abstraction, and easier to undo.

### Article IV — Integration-First

Contracts and integration points are designed and tested before internals are
polished. Acceptance tests exercise the package the way a consuming project
touches it, not the way its internals are arranged.

### Article V — Security & data-safety

Values interpolated into rendered output are escaped through the template
layer, never by hand-built string interpolation of model or user data. Secrets
live in runtime configuration, never in code, fixtures, or version control.
Authentication, authorisation, cryptography, and permission changes are never
fast-lane work.

### Article VI — Documentation

A public API change ships its documentation in the same pull request: README
and CHANGELOG updated. Docstrings, component annotations and code comments
follow
[`docs/contributing/standards/code-documentation.md`](docs/contributing/standards/code-documentation.md).
If the repository builds documentation, it builds clean. The README is written
for someone deciding whether to install this, and its links are absolute so
they resolve on the package index as well as on the repository page.

### Article VII — Dependency discipline

A new runtime dependency needs a stated justification — Article II applied to
the dependency tree. Development tooling comes from the shared bundle rather
than being pinned here package by package. `deptry` passes: nothing unused,
nothing missing, nothing relied on transitively.

### Article VIII — Internationalization

User-facing strings are translatable. In Python — models, forms, views, admin,
template tags, validators — they are wrapped with `gettext_lazy`, imported as
`_`. Templates `{% load i18n %}` and wrap strings with
`{% trans %}` or `{% blocktrans %}`.

Model `verbose_name` and `verbose_name_plural`, and form `label`, `help_text`
and `error_messages`, use `gettext_lazy`. Pure acronyms are exempt. A package
with user-facing strings ships a base English catalogue and a `locale/`
directory so a consuming project can compile or extend the translations. A
hard-coded user-visible string is a blocking review comment.

A package with no user-facing strings satisfies this trivially, and should not
carry an empty `locale/` directory to look as though it does.

### Article IX — Data-model conventions

Every model field is a deliberate indexing decision. A consuming project cannot
add indexes to a packaged model, so any field with a plausible lookup, filter,
or ordering path is indexed where it is defined — `db_index`, `unique`, a
foreign key's automatic index, or a composite entry in `Meta.constraints` or
`Meta.indexes`. A field with no query path stays unindexed, because an index
costs on every write. Either way the choice is recorded with the change.

`verbose_name` and `help_text` are mandatory on every model field. A field
without them produces an admin and an auto-generated form that read like a
database schema.

Migrations are consolidated per pull request: the migrations a branch
introduces are squashed into as few files as possible before it is submitted.
They are branch-local and unapplied anywhere, so this is safe at any stage.
Data migrations are exempt from regeneration — keep them.

### Article X — Cohesion

Related behaviour is grouped in a class, not scattered across module-level
functions.

**The test:** two or more module-level functions that share a *subject* belong
on a class. They share a subject when they operate on the same data, take the
same first argument, are only meaningful in sequence, or are named around the
same noun — `build_x`, `validate_x`, `render_x`.

**Why this is a standard and not a taste.** In a published package, a class is
the extension point. A consumer who needs different behaviour subclasses it and
overrides one method. A module of functions can only be monkey-patched, which
is not a supported interface and breaks on any internal change. Grouping also
gives the behaviour a name, a place for shared configuration, and one import
instead of six.

**Shape:** shared state or configuration → a regular class holding it.
Grouping for namespacing with no shared state → still a class, with
`@classmethod` or `@staticmethod`, or a small frozen dataclass carrying the
configuration. Expose a module-level convenience function only as a thin
wrapper over the class, never as the implementation.

**Django first.** Where the framework already owns the grouping, use it rather
than inventing a class: a `QuerySet` or `Manager` method instead of a function
taking a queryset, a model method or property instead of a function taking an
instance, a `Form` or `Serializer` method instead of a free validation
function, a view method instead of a helper the view calls.

**Exceptions, stated rather than assumed.** A genuinely standalone pure
function with no siblings. Framework-dictated module shapes: `conftest.py`
fixtures, migrations, `urls.py`, `apps.py`, decorator-registered template tags
and filters, signal receivers, management command entry points. Factory
functions that return the class. A module of independent utilities that
genuinely share no subject.

**This does not license abstraction.** Article III still holds: one class
grouping today's behaviour is the goal, not a base class, a registry, or a
hierarchy built for a second implementation that does not exist.

## Project articles

### Article XI — Compatibility

The public API is semver-stable. A deprecation lives one minor version with a
warning before it is removed, and the CHANGELOG says what replaces it.

### Article XII — Upstream does the work

Every account, sign-in and token behaviour comes from the package that already
implements it: the integrated authentication package for accounts and sign-in
(django-allauth is the only one supported today), Django REST framework and
its token package for API access. This package configures them, renders their pages
through django-mvp's application shell, and places them in its menus. It never
reimplements one of their features, subclasses one of their models, or ships a
form that replaces theirs where overriding a template would do.

A feature the upstream package does not have is raised there first. Building it
here is a decision recorded under `docs/adr/`, with the upstream issue linked.

Each upstream dependency is bounded to the major versions CI actually runs
against, because this package renders their templates and a major release can
rename the context those templates receive.

### Article XIII — Optional capabilities are gated on installation

API access exists only when the host project has installed Django REST
framework. The package imports, its pages render and its menus build in a
project without it, and a test asserts that. Nothing Django REST framework
needs is imported at module level outside the code that only runs when it is
present, and it is an optional extra, never a hard dependency.

The same rule applies to any later capability that depends on a package a host
project may not want.

### Article XIV — Scope

This package is about a person's access to their own account. It does not
decide what a signed-in person may do: permissions, roles, groups and
object-level authorisation are the host project's, and a pull request adding
them is out of scope however small it is.

It does not issue tokens to third-party applications on a person's behalf.
That is OAuth, a separate protocol with its own consent and client model, and
it belongs in its own package if one is ever needed.

## Quality bar

Read at planning and at review; applies to every change.

- Test coverage meets the floors in
  `docs/contributing/standards/testing.md`, and `codecov.yml` is the
  reference.
- Every public API change updates README and CHANGELOG in the same pull
  request.
- Lint, type-check, and `deptry` pass.
- The package builds and its metadata is valid; the README renders on the
  package index; the public API honours the deprecation policy.

## Non-negotiables

- Tests, build and lint pass before a change merges. Nobody overrides a red
  check.
- The default branch requires one approval, and the author of a change never
  approves it.

<!--
  The footer below is mandatory and closes this file, so a review can name the
  revision it was made against. The format is fixed: bold labels with the colon
  outside the bold, ISO dates, and the last line of the file.

  Versioning is semantic. MAJOR for a removed or redefined article, MINOR for a
  new article or materially expanded guidance, PATCH for clarification and
  wording. Every amendment updates the version and the Last Amended date.
  Ratified never changes after first adoption.
-->

---

**Version**: 2.0.0 | **Ratified**: 2026-09-24 | **Last Amended**: 2026-09-28
