"""Account adapters that put allauth in a state the demo is never in."""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from demo.adapter import DemoAccountAdapter


class ClosedSignupAdapter(DemoAccountAdapter):
    """The demo's adapter, with sign-up switched off."""

    def is_open_for_signup(self, request):
        return False


class NoProvidersSocialAdapter(DefaultSocialAccountAdapter):
    """A social adapter that lists no provider, as a project with none configured."""

    def list_providers(self, request):
        return []
