"""Account adapters that put allauth in a state the demo is never in."""

from demo.adapter import DemoAccountAdapter


class ClosedSignupAdapter(DemoAccountAdapter):
    """The demo's adapter, with sign-up switched off."""

    def is_open_for_signup(self, request):
        return False
