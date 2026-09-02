from __future__ import annotations

import logging

from celery import Task, shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(
    self: Task[..., None],
    subject: str,
    message: str,
    recipient_list: list[str],
) -> None:
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=recipient_list,
        )
    except Exception as exc:
        logger.warning("Email delivery failed, retrying: %s", exc)
        raise self.retry(exc=exc) from exc
