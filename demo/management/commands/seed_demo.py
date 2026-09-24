"""Put the demo project into a state every page can be looked at from.

Three sign-ins, because the application shell renders differently for each: an
ordinary account, one with access to the admin, and one with everything. A
reviewer opening this project should not have to invent a login or read the
code to find out what exists.

Safe to run repeatedly, and refuses to run at all unless DEBUG is on — these
are known passwords, and the only thing standing between them and a deployed
site is that this command will not execute there.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

PASSWORD = "password"

ACCOUNTS = [
    ("regular.user@example.com", {"is_staff": False, "is_superuser": False}),
    ("staff.user@example.com", {"is_staff": True, "is_superuser": False}),
    ("super.user@example.com", {"is_staff": True, "is_superuser": True}),
]


class Command(BaseCommand):
    help = "Create the demo sign-in accounts."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo creates accounts with a known password and only "
                "runs with DEBUG on."
            )

        user_model = get_user_model()
        # The address is the identifier whichever field the project made its
        # username, so a project that swapped in a custom user model still gets
        # three accounts rather than an integrity error.
        username_field = user_model.USERNAME_FIELD

        for email, flags in ACCOUNTS:
            user, created = user_model.objects.get_or_create(
                **{username_field: email}, defaults={"email": email, **flags}
            )
            for attribute, value in flags.items():
                setattr(user, attribute, value)
            user.set_password(PASSWORD)
            user.save()
            self.stdout.write(f"  {'created' if created else 'updated'}  {email}")

        self.stdout.write(
            self.style.SUCCESS(f"\nAll three sign in with the password {PASSWORD!r}.")
        )
