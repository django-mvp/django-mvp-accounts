# Decisions — 006 Organisations

The reading below was put to the maintainer on 2026-11-08 and confirmed as written, including the
three suggestions it carried: handing over ownership, reminding invitees, and a way for a view to
get the current organisation. Each place the issue was silent is recorded here with the reading
chosen.

## D1 — Roles are django-organizations' own

One owner, then admins and members. The owner is also an admin. No further roles, because a role
here only says who runs the organisation (Article XIV), and django-organizations already models
exactly that.

## D2 — Every signed-in person may create an organisation, unless the project says otherwise

The same shape as `MVP_ACCOUNTS_API_TOKEN_ACCESS` in FS-005: one setting naming a function of the
project's. A school site may want only teachers to create classes.

## D3 — An invitee without an account signs up through the site's own sign-up

django-organizations' model-tracked invitations route a person who is not signed in to its own
registration form, which creates the account itself. That would bypass allauth's sign-up, its email
verification and social sign-in, and draw a form this package would have to style and keep in step
with allauth. The invitation instead sends the person to sign in or sign up, and brings them back to
the invitation afterwards.

## D4 — Only the invited address can accept an invitation

django-organizations lets any signed-in person who opens an invitation link accept it, apart from
the person who sent it. A forwarded or leaked link would then admit whoever holds it. Accepting is
limited to a signed-in person whose account holds the invited address. Someone invited at one
address who signs up with another adds the invited address to their account first, or is invited
again. This is the reading most open to veto: it trades a little convenience for knowing who joins.

## D5 — The current organisation lasts for the browser session

Not saved to the account, so it needs no model (ADR 0007). On a fresh sign-in the person starts in
their first organisation by name, which is stable and needs nothing remembered.

## D6 — The owner cannot leave, and handing over ownership is built here

django-organizations has `change_owner()` and no page for it. Without one, an owner could never
leave, so the reading includes a handover page. The former owner stays on as an admin, since
removing them is a separate, deliberate step any admin can take.

## D7 — Parts built here need a decision record

Leaving, handing over ownership, the current organisation and switching, and joining after the
site's own sign-up are features django-organizations does not have. Article XII asks for each to be
recorded under `docs/adr/` (FR-018). No upstream issue is proposed: the current organisation is
application state, and the other three are small additions over methods django-organizations
already has.

## D8 — Withdrawing and expiring invitations are left out

django-organizations has neither. The issue does not ask for them, and an invitation that is never
accepted does no harm.
