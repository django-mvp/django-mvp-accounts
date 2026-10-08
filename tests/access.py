"""Access functions a host project could name, for the tests that need one."""

from django.contrib.auth.models import AbstractBaseUser

asked: list[AbstractBaseUser] = []


def staff_only(user: AbstractBaseUser) -> bool:
    """Let in staff only, and note who was asked."""
    asked.append(user)
    return bool(user.is_staff)


def returns_none(user: AbstractBaseUser) -> None:
    """Answer with something falsy that is not a bool."""
    return None
