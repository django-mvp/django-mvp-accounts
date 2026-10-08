"""Who may hold API tokens, as the project decides it."""

from django.conf import settings
from django.utils.module_loading import import_string


def may_use_tokens(user) -> bool:
    """Say whether ``user`` may see and use the API tokens pages.

    Every signed-in person may, unless the project names a callable in
    ``MVP_ACCOUNTS_API_TOKEN_ACCESS``. The callable takes the user and returns
    whether they may.

    Args:
        user: The person asking, signed in or not.

    Returns:
        ``True`` when the pages, the menu entry and the card are theirs to see.
    """
    if not user.is_authenticated:
        return False
    path = getattr(settings, "MVP_ACCOUNTS_API_TOKEN_ACCESS", None)
    if path is None:
        return True
    return bool(import_string(path)(user))
