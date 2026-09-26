"""An email backend that keeps what the demo sends, for the outbox page."""

from django.core.mail.backends.base import BaseEmailBackend

from demo.models import SentMessage


class OutboxEmailBackend(BaseEmailBackend):
    """Stores each message as a :class:`demo.models.SentMessage`.

    The body kept is the plain-text one, which is where allauth puts its links
    and codes.
    """

    def send_messages(self, email_messages):
        for message in email_messages:
            SentMessage.objects.create(
                recipient=", ".join(message.to),
                subject=message.subject,
                body=message.body,
            )
        return len(email_messages)
