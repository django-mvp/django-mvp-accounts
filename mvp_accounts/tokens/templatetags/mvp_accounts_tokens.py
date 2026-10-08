"""Template tags for the API tokens pages."""

from django import template

from mvp_accounts.tokens.access import may_use_tokens

register = template.Library()


@register.simple_tag(takes_context=True)
def may_use_api_tokens(context) -> bool:
    """Say whether the person viewing the page may use API tokens."""
    request = context.get("request")
    return request is not None and may_use_tokens(request.user)
