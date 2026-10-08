"""Who may hold API tokens in the demo."""


def staff_only(user) -> bool:
    """Let staff hold API tokens and nobody else."""
    return user.is_staff
