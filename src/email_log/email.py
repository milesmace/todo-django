"""
Email backend that logs all emails to the database and dispatches
Celery tasks for async delivery.

Usage:
    Set EMAIL_BACKEND = 'email_log.email.EmailLogBackend' in settings.
    Optionally set EMAIL_ACTUAL_BACKEND for the real SMTP backend.
"""

from django.core.mail.backends.base import BaseEmailBackend

from .models import EmailLog, EmailLogMessage


class EmailLogBackend(BaseEmailBackend):
    """
    An email backend that logs emails and dispatches async Celery tasks.

    When send_messages() is called:
    1. Creates EmailLogMessage records for each email
    2. Creates EmailLog records for all recipients (to/cc/bcc)
    3. Queues a Celery task for each email log
    4. Returns immediately (fire-and-forget)

    The actual email delivery happens asynchronously via Celery workers.
    """

    def send_messages(self, email_messages):
        """
        Log email messages and dispatch Celery tasks for delivery.

        Args:
            email_messages: List of EmailMessage objects to send.

        Returns:
            Number of email logs queued for delivery.
        """
        from .tasks import send_email_to_recipient

        if not email_messages:
            return 0

        num_logs = 0

        for message in email_messages:
            # Create the log message record
            log_message = EmailLogMessage.objects.create(
                subject=message.subject,
                body=message.body,
                from_email=message.from_email,
            )

            # Create email log records and queue tasks
            email_logs_to_create = []

            # Collect all recipients by type
            for email in message.to:
                email_logs_to_create.append(
                    EmailLog(
                        email_log_message=log_message,
                        to_email=email,
                        recipient_type=EmailLog.RecipientType.TO,
                        status=EmailLog.Status.PENDING,
                    )
                )

            for email in message.cc:
                email_logs_to_create.append(
                    EmailLog(
                        email_log_message=log_message,
                        to_email=email,
                        recipient_type=EmailLog.RecipientType.CC,
                        status=EmailLog.Status.PENDING,
                    )
                )

            for email in message.bcc:
                email_logs_to_create.append(
                    EmailLog(
                        email_log_message=log_message,
                        to_email=email,
                        recipient_type=EmailLog.RecipientType.BCC,
                        status=EmailLog.Status.PENDING,
                    )
                )

            # Bulk create all email logs
            created_logs = EmailLog.objects.bulk_create(email_logs_to_create)

            # Queue a Celery task for each email log
            for email_log in created_logs:
                send_email_to_recipient.delay(email_log.id)

            num_logs += len(created_logs)

        return num_logs
