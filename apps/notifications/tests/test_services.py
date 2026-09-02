from django.core import mail

from apps.notifications.services import NotificationService


def test_send_email_queues_and_delivers_the_message() -> None:

    NotificationService.send_email(
        subject="Order confirmed",
        message="Your order has been placed.",
        recipient_list=["shopper@example.com"],
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Order confirmed"
