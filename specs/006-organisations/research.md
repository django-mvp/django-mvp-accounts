# Research — 006 Organisations

## Assumptions checked

Run on 2026-11-09, before the specification gate.

- **django-organizations 2.7.0 runs on this package's newest Django.** Installed alongside the
  package's own environment (Django 6.1.2) with `organizations` in `INSTALLED_APPS`: its migrations
  apply, `makemigrations --check organizations` reports no changes, an organisation can be created,
  `add_user()` makes the first person owner, `change_owner()` hands ownership over, and a
  model-tracked invitation is created with its own link identifier.
- **It brings django-extensions with it.** django-extensions 4.1 is installed as its dependency,
  for the slug field.
- **Its pages and their permissions are as the specification reads them.** From the 2.7.0 source:
  listing and creating need a signed-in person, viewing an organisation and its members list need
  membership, renaming, inviting, reminding, editing and removing a member need an admin, and
  deleting needs the owner. There is no view for leaving, for handing over ownership or for a
  current organisation.
- **Its invitation flow for a new person uses its own registration form.** `ModelInvitation`
  renders `UserRegistrationForm` for a person who is not signed in, and lets any signed-in person
  other than the sender accept. Both are why D3 and D4 exist.
- **The Account Center takes another entry and card the way the API tokens pages do.** FS-005's
  entry and card, drawn only when their URLs resolve, are on main and covered by tests.
