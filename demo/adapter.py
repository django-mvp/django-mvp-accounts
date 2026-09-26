"""The demo's account adapter.

allauth has no model of its own for phone numbers, so a project that turns them
on says where they are kept. The demo keeps them in one table and prints the
code it would have texted.
"""

from allauth.account.adapter import DefaultAccountAdapter

from demo.models import PhoneNumber


class DemoAccountAdapter(DefaultAccountAdapter):
    """Stores phone numbers in :class:`demo.models.PhoneNumber`."""

    def set_phone(self, user, phone, verified):
        PhoneNumber.objects.update_or_create(
            user=user, defaults={"number": phone, "verified": verified}
        )

    def get_phone(self, user):
        stored = PhoneNumber.objects.filter(user=user).first()
        if stored is None:
            return None
        return stored.number, stored.verified

    def set_phone_verified(self, user, phone):
        # allauth finishes a change by calling this with the new number, which
        # it has not stored first, so marking it verified stores it too.
        self.set_phone(user, phone, verified=True)

    def get_user_by_phone(self, phone):
        stored = PhoneNumber.objects.filter(number=phone).select_related("user").first()
        return stored.user if stored else None

    def send_verification_code_sms(self, user, phone, code, **kwargs):
        print(f"SMS to {phone}: your verification code is {code}")
