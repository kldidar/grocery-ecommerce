from apps.notifications.tasks import send_email_task


class NotificationService:
    @staticmethod
    def send_email(subject: str, message: str, recipient_list: list[str]) -> None:

        send_email_task.delay(subject, message, recipient_list)
