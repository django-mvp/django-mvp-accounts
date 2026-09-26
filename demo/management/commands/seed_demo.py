"""Put the demo project into a state every page can be looked at from.

Three sign-ins, because the application shell renders differently for each: an
ordinary account, one with access to the admin, and one with everything. A
fourth, social.user@example.com, has no password and signs in only through the
test provider. The staff account has a connected test provider account with uid
1001, and social.user's has uid 2002. Signed in as staff, the connections page
shows an account that can be removed. Signed in as social.user, it shows one that
allauth refuses to remove. A reviewer opening
this project should not have to invent a login or read the code to find out
what exists.

Safe to run repeatedly, and refuses to run at all unless DEBUG is on — these
are known passwords, and the only thing standing between them and a deployed
site is that this command will not execute there.
"""

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from demo.models import PhoneNumber

PASSWORD = "password"

SOCIAL_EMAIL = "social.user@example.com"
STAFF_UID = "1001"
SOCIAL_UID = "2002"
PROVIDER = "dummy"

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
            self.style.SUCCESS(
                f"\nThe first three sign in with the password {PASSWORD!r}. "
                f"{SOCIAL_EMAIL} has no password and signs in through the test "
                f"provider as uid {SOCIAL_UID}; staff.user@example.com has uid "
                f"{STAFF_UID} connected."
            )
        )

    def seed_states(self, user_model, username_field):
        """Give the accounts what the account pages have to show.

        The staff account has a second, unverified address, so the email page
        lists several with their badges and actions. The super account has a
        verified phone number, so the phone page shows one to change. The staff
        account has a connected test provider account it can remove. A fourth
        account with no password has one too, and allauth refuses to remove it,
        because it is that account's only way in.
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
        SocialAccount.objects.get_or_create(
            user=staff, provider=PROVIDER, uid=STAFF_UID
        )
        self.seed_social_user(user_model, username_field)

    def seed_social_user(self, user_model, username_field):
        """Create the account that has no password and one connected account."""
        user, created = user_model.objects.get_or_create(
            **{username_field: SOCIAL_EMAIL}, defaults={"email": SOCIAL_EMAIL}
        )
        user.set_unusable_password()
        user.save()
        EmailAddress.objects.update_or_create(
            user=user,
            email=SOCIAL_EMAIL,
            defaults={"verified": True, "primary": True},
        )
        SocialAccount.objects.get_or_create(
            user=user, provider=PROVIDER, uid=SOCIAL_UID
        )
        self.stdout.write(f"  {'created' if created else 'updated'}  {SOCIAL_EMAIL}")
