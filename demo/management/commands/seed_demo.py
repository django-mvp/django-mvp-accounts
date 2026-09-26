"""Put the demo project into a state every page can be looked at from.

Three sign-ins, because the application shell renders differently for each: an
ordinary account, one with access to the admin, and one with everything. A
reviewer opening this project should not have to invent a login or read the
code to find out what exists.

Safe to run repeatedly, and refuses to run at all unless DEBUG is on — these
are known passwords, and the only thing standing between them and a deployed
site is that this command will not execute there.
"""

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from demo.models import PhoneNumber

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
            # allauth refuses to sign in an account whose address is not
            # verified, so each account gets one that is, marked primary.
            EmailAddress.objects.update_or_create(
                user=user,
                email=email,
                defaults={"verified": True, "primary": True},
            )
            self.stdout.write(f"  {'created' if created else 'updated'}  {email}")

        self.seed_states(user_model, username_field)

        self.stdout.write(
            self.style.SUCCESS(f"\nAll three sign in with the password {PASSWORD!r}.")
        )

    def seed_states(self, user_model, username_field):
        """Give the accounts what the account pages have to show.

        The staff account has a second, unverified address, so the email page
        lists several with their badges and actions. The super account has a
        verified phone number, so the phone page shows one to change.
        """
        staff = user_model.objects.get(**{username_field: "staff.user@example.com"})
        EmailAddress.objects.get_or_create(
            user=staff,
            email="staff.user+second@example.com",
            defaults={"verified": False, "primary": False},
        )
        admin = user_model.objects.get(**{username_field: "super.user@example.com"})
        PhoneNumber.objects.update_or_create(
            user=admin, defaults={"number": "+4915100000001", "verified": True}
        )
