"""Who may hold API tokens, as the host project decides it.

This module reads one Django setting and imports nothing from django-rest-knox
or Django REST framework, so the menu entry and the Account Center card can call
it in a project that has neither.
"""

from django.conf import settings
from django.utils.module_loading import import_string


def may_use_tokens(user) -> bool:
    """Say whether ``user`` may see and use the API tokens pages.

    Every signed-in person may, unless the host project names a function in
    ``MVP_ACCOUNTS_API_TOKEN_ACCESS``. That function takes the user and says
    whether they may.

    Args:
        user: The person asking, signed in or not.

    Returns:
        ``False`` for a visitor who is not signed in, without asking the host
        project's function. ``True`` when the setting is unset or ``None``.
        Otherwise the truth of the function's answer.

    Raises:
        ImportError: The setting names a path that does not import.
    """
    if not user.is_authenticated:
        return False
    path = getattr(settings, "MVP_ACCOUNTS_API_TOKEN_ACCESS", None)
    if path is None:
        return True
    return bool(import_string(path)(user))
