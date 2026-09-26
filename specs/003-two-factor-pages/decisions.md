# Decisions — 003 Two-factor authentication

## D1 — Reskinned elements keep allauth's ids and data attributes

allauth's security-key and passkey pages are driven by its own JavaScript, which looks up buttons,
hidden inputs, forms and its JSON configuration by id and by `data-allauth-onload`. A reskin that
drops one of those renders a page that looks right and does nothing when the button is pressed.
Keeping every id and data attribute allauth passes an element is the whole rule, and a test per page
checks the hooks are present. FS-001's field element forwards a fixed list of attributes. Where the
multi-factor pages pass one that list does not include, this feature extends the element.

## D2 — The QR code is always dark on light

Authenticator apps read QR codes as dark modules on a light background, and many cannot read an
inverted one. allauth renders the code as an image, so it keeps a light background in every theme
rather than following the page's colours.

## D3 — HTTPS for the dev server stays out of scope

Browsers only allow WebAuthn over HTTPS or on `localhost`, so security keys and passkeys cannot be
tried on the dev server's plain HTTP tailnet address. The pages and their script hooks are covered by
tests. Giving the dev server an HTTPS address is general tooling, not part of this feature.

## D4 — Passkey sign-up is specified here

`account/signup_by_passkey.html` ships in allauth's account app but only exists when the
multi-factor app is installed with passkey sign-up enabled. FS-001 left it to this feature.
