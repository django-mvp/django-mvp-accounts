# Planning notes — 005 Personal API tokens

Suggestions and open questions from the maintainer for whoever plans this feature. Each one must
be investigated and answered by name in the research and the plan, as adopted or not adopted with
the reason. They are inputs to answer, not instructions to follow.

## A way to name a token

**From the maintainer, reviewing the prototype on 2026-10-08.** A person should be able to give a
token a name, so they know later what each one was made for. Naming tokens is standard practice
where people hold several.

What is known:

- django-rest-knox stores no name. Its token record holds a hash, the first characters of the
  token, the owner, a creation time and an expiry.
- The specification as it stands provides no names (`decisions.md`, D4) and adds no model or
  migration (FR-012). The list tells tokens apart by their first characters and their dates.
- The maintainer has ruled out deciding in the prototype that this package gets a model or an app
  of its own to hold names. That is not a ruling on the answer. It is a ruling on where the answer
  is made: in planning, and then in review.

What is asked of the plan:

- Research the ways a name could be provided and what each costs a host project, and answer this
  note by name.
- Raise the answer at review, whichever way it goes, so the maintainer decides it there.
- If the answer changes what the specification says, amend the specification and have the
  maintainer approve the change before building it.

No mechanism is proposed here.
