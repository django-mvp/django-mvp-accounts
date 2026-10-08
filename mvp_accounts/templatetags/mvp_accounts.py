"""Template tags for this package's account pages.

Nothing here imports django-rest-knox or Django REST framework, so the Account
Center renders in a project that has neither.
"""

from django import template

from mvp_accounts.tokens.access import may_use_tokens

register = template.Library()


@register.simple_tag(takes_context=True)
def may_use_api_tokens(context) -> bool:
    """Say whether the person viewing the page may use API tokens.

    Args:
        context: The template context, which holds the request when the page
            was rendered for one.

    Returns:
        ``True`` when the host project lets this request's user hold tokens,
        and ``False`` when there is no request.
    """
    request = context.get("request")
    return request is not None and may_use_tokens(request.user)
