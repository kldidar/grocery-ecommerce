from django.core import mail

from apps.notifications.tasks import send_email_task


def test_send_email_task_delivers_via_the_email_backend() -> None:

    send_email_task(
        subject="Welcome",
        message="Thanks for signing up.",
        recipient_list=["shopper@example.com"],
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Welcome"
    assert mail.outbox[0].to == ["shopper@example.com"]


def test_send_email_task_can_be_dispatched_through_celery() -> None:

    result = send_email_task.delay(
        subject="Welcome",
        message="Thanks for signing up.",
        recipient_list=["shopper@example.com"],
    )
    assert result.successful()
