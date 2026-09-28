"""The demo's account adapter, which keeps phone numbers and texted codes."""

from allauth.account.adapter import DefaultAccountAdapter

from demo.models import PhoneNumber, SentMessage


class DemoAccountAdapter(DefaultAccountAdapter):
    """Store phone numbers in :class:`demo.models.PhoneNumber`.

    allauth has no model of its own for phone numbers, so a project that turns
    them on says where they are kept. The code it would have texted goes to the
    outbox.
    """

    def set_phone(self, user, phone, verified):
        """Store the number in the demo's table."""
        PhoneNumber.objects.update_or_create(
            user=user, defaults={"number": phone, "verified": verified}
        )

    def get_phone(self, user):
        """Read the number from the demo's table."""
        stored = PhoneNumber.objects.filter(user=user).first()
        if stored is None:
            return None
        return stored.number, stored.verified

    def set_phone_verified(self, user, phone):
        """Store the number as verified."""
        # allauth finishes a change by calling this with the new number, which
        # it has not stored first, so marking it verified stores it too.
        self.set_phone(user, phone, verified=True)

    def get_user_by_phone(self, phone):
        """Find the user through the demo's table."""
        stored = PhoneNumber.objects.filter(number=phone).select_related("user").first()
        return stored.user if stored else None

    def send_verification_code_sms(self, user, phone, code, **kwargs):
        """Print the code and keep it in the outbox."""
        print(f"SMS to {phone}: your verification code is {code}")
        SentMessage.objects.create(
            recipient=phone,
            subject="Text message",
            body=f"Your verification code is {code}",
        )
