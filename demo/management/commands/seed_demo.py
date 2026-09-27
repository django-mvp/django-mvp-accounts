"""Put the demo project into a state every page can be looked at from.

Three sign-ins, because the application shell renders differently for each: an
ordinary account, one with access to the admin, and one with everything. A
fourth, social.user@example.com, has no password and signs in only through the
test provider. The staff account has a connected test provider account with uid
1001, and social.user's has uid 2002. Signed in as staff, the connections page
shows an account that can be removed. Signed in as social.user, it shows one that
allauth refuses to remove. regular.user is also signed in from two other
browsers, so signing in as that account shows three sessions on the sessions
page and offers to sign out the others. Any other account shows one. A reviewer
opening this project should not have to invent a login or read the code to find
out what exists.

Safe to run repeatedly, and refuses to run at all unless DEBUG is on — these
are known passwords, and the only thing standing between them and a deployed
site is that this command will not execute there.
"""

from datetime import timedelta

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.usersessions.models import UserSession
from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)
from django.contrib.sessions.backends.db import SessionStore
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from demo.models import PhoneNumber

PASSWORD = "password"

SOCIAL_EMAIL = "social.user@example.com"
STAFF_UID = "1001"
SOCIAL_UID = "2002"
PROVIDER = "dummy"

# The two other browsers regular.user is signed in from: an address from
# documentation ranges, a browser string, and how many days ago each started.
OTHER_BROWSERS = [
    (
        "192.0.2.10",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 "
        "Safari/604.1",
        2,
    ),
    (
        "198.51.100.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        5,
    ),
]

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
                f"{STAFF_UID} connected. regular.user@example.com is signed in from two "
                "other browsers, so its sessions page lists three."
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
        regular = user_model.objects.get(**{username_field: ACCOUNTS[0][0]})
        self.seed_sessions(regular)

    def seed_sessions(self, user):
        """Sign ``user`` in from two other browsers, replacing the last run's.

        Each is a saved Django session, because allauth drops a recorded session
        whose Django session is gone before it lists any. The password hash is
        read from the saved user, since setting the password changes it and
        allauth drops a session whose hash no longer matches. The earlier ones
        are ended rather than deleted, so their Django sessions go with them.
        """
        earlier = UserSession.objects.filter(
            user=user, ip__in=[ip for ip, _agent, _days in OTHER_BROWSERS]
        )
        for session in earlier:
            session.end()
        for ip, user_agent, days_ago in OTHER_BROWSERS:
            store = SessionStore()
            store[SESSION_KEY] = user._meta.pk.value_to_string(user)
            store[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
            store[HASH_SESSION_KEY] = user.get_session_auth_hash()
            store.save()
            started = timezone.now() - timedelta(days=days_ago)
            UserSession.objects.create(
                user=user,
                session_key=store.session_key,
                ip=ip,
                user_agent=user_agent,
                created_at=started,
                last_seen_at=started,
            )

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
