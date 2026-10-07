"""Put the demo project into a state every page can be looked at from.

Three sign-ins, because the application shell renders differently for each: an
ordinary account, one with access to the admin, and one with everything. A
fourth, mfa.user@example.com, has an authenticator app and recovery codes, so
signing in ends at the second-factor step. The demo's fixed code, set in
MFA_TOTP_INSECURE_BYPASS_CODE, passes that step, and it is a convenience for this
demo only. A fifth, social.user@example.com, has no password and signs in only
through the test provider. The staff account has a connected test provider account with uid
1001, and social.user's has uid 2002. Signed in as staff, the connections page
shows an account that can be removed. Signed in as social.user, it shows one that
allauth refuses to remove. regular.user is also signed in from two other
browsers, so signing in as that account shows three sessions on the sessions
page and offers to sign out the others. Any other account shows one.
regular.user also holds three API tokens, one of which never expires, and a
fourth that has expired and is not listed. staff.user holds none, and
super.user holds as many as the demo allows. A reviewer
opening this project should not have to invent a login or read the code to find
out what exists.

Safe to run repeatedly, and refuses to run at all unless DEBUG is on — these
are known passwords, and the only thing standing between them and a deployed
site is that this command will not execute there.
"""

from datetime import timedelta
from importlib import import_module

from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import TOTP
from allauth.socialaccount.models import SocialAccount
from allauth.usersessions.models import UserSession
from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from knox.models import get_token_model
from knox.settings import knox_settings

from demo.models import PhoneNumber

PASSWORD = "password"

MFA_EMAIL = "mfa.user@example.com"
# A fixed secret, so the account's authenticator app is the same after every run.
MFA_SECRET = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
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

# regular.user's API tokens: how many days ago each was created, and how many
# days from now it expires. None never expires, and a negative number already has.
REGULAR_TOKENS = [(40, None), (6, 24), (0, 30), (45, -15)]

ACCOUNTS = [
    ("regular.user@example.com", {"is_staff": False, "is_superuser": False}),
    ("staff.user@example.com", {"is_staff": True, "is_superuser": False}),
    ("super.user@example.com", {"is_staff": True, "is_superuser": True}),
]


class Command(BaseCommand):
    """Create the demo's sign-in accounts and the states they show."""

    help = "Create the demo sign-in accounts."

    def handle(self, *args, **options):
        """Refuse to run without DEBUG, then seed every account."""
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
        self.seed_two_factor_user(user_model, username_field)
        self.seed_tokens(user_model, username_field)

        bypass = settings.MFA_TOTP_INSECURE_BYPASS_CODE
        second_factor = (
            f"the demo's fixed code {bypass!r} passes that step, as a demo "
            "convenience only"
            if bypass
            else "no fixed code is set, so enter a code computed from its secret"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"\nThe first three sign in with the password {PASSWORD!r}, and so "
                f"does {MFA_EMAIL}, which then asks for a second factor: "
                f"{second_factor}. "
                f"{SOCIAL_EMAIL} has no password and signs in through the test "
                f"provider as uid {SOCIAL_UID}; staff.user@example.com has uid "
                f"{STAFF_UID} connected. regular.user@example.com is signed in from two "
                "other browsers, so its sessions page lists three, and holds "
                "three API tokens. staff.user@example.com holds none and "
                "super.user@example.com holds as many as the demo allows."
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
        Like any Django session they expire after two weeks, and running the
        command again brings them back.
        """
        earlier = UserSession.objects.filter(
            user=user, ip__in=[ip for ip, _agent, _days in OTHER_BROWSERS]
        )
        for session in earlier:
            session.end()
        for ip, user_agent, days_ago in OTHER_BROWSERS:
            store = import_module(settings.SESSION_ENGINE).SessionStore()
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

    def seed_tokens(self, user_model, username_field):
        """Give the three accounts the token lists the tokens page has to show.

        Every run replaces them, so a token revoked while looking at the page
        comes back. The values are thrown away, as they are for anyone: a token
        to try against the API is made on the page.
        """
        token_model = get_token_model()
        regular, staff, admin = (
            user_model.objects.get(**{username_field: email}) for email, _ in ACCOUNTS
        )
        token_model.objects.filter(user__in=[regular, staff, admin]).delete()
        now = timezone.now()
        for created_days_ago, expires_in_days in REGULAR_TOKENS:
            token, _value = token_model.objects.create(user=regular, expiry=None)
            # `created` is set on save, so it is moved back afterwards.
            token_model.objects.filter(pk=token.pk).update(
                created=now - timedelta(days=created_days_ago, hours=3),
                expiry=(
                    None
                    if expires_in_days is None
                    else now + timedelta(days=expires_in_days)
                ),
            )
        for number in range(knox_settings.TOKEN_LIMIT_PER_USER or 0):
            token, _value = token_model.objects.create(user=admin)
            token_model.objects.filter(pk=token.pk).update(
                created=now - timedelta(days=number * 4, hours=1),
                expiry=now + timedelta(days=30 - number * 4),
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

    def seed_two_factor_user(self, user_model, username_field):
        """Create the account whose sign-in ends at the second-factor step."""
        user, created = user_model.objects.get_or_create(
            **{username_field: MFA_EMAIL}, defaults={"email": MFA_EMAIL}
        )
        user.set_password(PASSWORD)
        user.save()
        EmailAddress.objects.update_or_create(
            user=user,
            email=MFA_EMAIL,
            defaults={"verified": True, "primary": True},
        )
        if not Authenticator.objects.filter(
            user=user, type=Authenticator.Type.TOTP
        ).exists():
            TOTP.activate(user, MFA_SECRET)
        if not Authenticator.objects.filter(
            user=user, type=Authenticator.Type.RECOVERY_CODES
        ).exists():
            RecoveryCodes.activate(user)
        self.stdout.write(f"  {'created' if created else 'updated'}  {MFA_EMAIL}")
