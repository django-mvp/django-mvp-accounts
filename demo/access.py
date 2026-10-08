"""Who may hold API tokens in the demo."""


def staff_only(user) -> bool:
    """Let in staff and nobody else, so the demo shows a site that limits tokens.

    Args:
        user: The signed-in person asking.

    Returns:
        Whether the person is staff.
    """
    return user.is_staff
