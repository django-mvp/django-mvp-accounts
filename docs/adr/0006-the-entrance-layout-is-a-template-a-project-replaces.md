# ADR 0006 — The entrance layout is a template a project replaces

**Status:** accepted

## Decision

A host project chooses how its entrance pages are laid out by writing one template,
`mvp_accounts/entrance/base.html`, which wraps the pieces of the page in a Cotton component.
There is no setting for it.

- `allauth/layouts/entrance.html` extends `mvp_accounts/entrance/base.html`, which extends
  `mvp_accounts/entrance/layout.html`. The first maps allauth's block names, the last holds the
  document and the pieces, and the one in the middle is the only file a project replaces.
- `layout.html` declares the pieces inside `{% block layout %}`, each as a Cotton slot filled from a
  Django block: `logo`, `title` (from the `heading` block), `providers`, the default slot (from
  `content`) and `footer`. A project's `base.html` overrides `layout` and writes
  `{{ block.super }}` inside the component it has chosen, next to any slots of its own.
- This package's own `base.html` wraps the pieces in `<c-mvp_accounts.entrance.card>`, the centred
  card, so a project that writes nothing sees one.
- The slot names are the ones the sign-in and sign-up page blocks in
  [daisy-cotton-ext](https://github.com/django-mvp/daisy-cotton-ext) take, so any of those blocks can
  be the component. The package does not depend on daisy-cotton-ext and ships no component built on
  it. A project that uses one installs it and links its stylesheet.
- `account/login.html` and `account/signup.html` are copies of allauth's pages, taken apart to fill
  `heading`, `providers`, `content` and `footer` separately. This adds two pages to the copies
  [ADR 0001](0001-reskin-allauth-through-its-templates.md) lists, and each names the allauth version
  it came from. Every other entrance page fills `content` alone and arrives whole.
- The `logo` block defaults to django-mvp's `<c-mvp.brand.logo>` linking home. A django-mvp project
  already declares its logo there, so no layout has to be told what it is.

## Why

A setting that named a layout was built first. It needed a template tag to read it, a dynamic
component to draw it, a wrapper component for every layout, and a way to carry a layout's attributes
through a settings dictionary. A project that wanted a different background still had to override a
template. Replacing one template does all of it with what Django and Cotton already provide: the
component is written as a tag, so its attributes and slots work as its own documentation says, and a
mistyped name raises instead of drawing nothing.

The component cannot be the thing that extends the document. Cotton renders a component as a
separate template, so the blocks an allauth page fills never reach it, and a component that declares
attributes cannot start with `{% extends %}` at all. The project's template therefore extends ours
and wraps the component around `{{ block.super }}`, which is where the page's blocks are.

allauth's sign-in and sign-up pages put the heading, the form, the passkey and code buttons and the
provider list in one block. A layout that sets the provider buttons apart from the form, or folds
the form away, needs them separately, and only a copy of the page can hand them over that way. The
form itself is still allauth's.

## Revisit if

Cotton gains a way for a component to take part in template inheritance, or allauth splits its
sign-in and sign-up pages into blocks a layout could place without a copy.
