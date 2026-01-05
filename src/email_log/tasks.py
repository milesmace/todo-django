"""
Celery tasks for async email delivery.

Each recipient gets their own task, allowing granular tracking and independent retries.
"""

from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def send_email_to_recipient(self, email_log_id: int) -> dict:
    """
    Send an email to a single recipient.

    This task is queued by EmailLogBackend for each recipient.
    It handles the actual SMTP delivery and updates the email log status.

    Args:
        email_log_id: The ID of the EmailLog record.

    Returns:
        dict with status and email_log_id
    """
    from email_log.models import EmailLog

    try:
        email_log = EmailLog.objects.select_related("email_log_message").get(
            id=email_log_id
        )
    except EmailLog.DoesNotExist:
        return {"status": "error", "message": f"EmailLog {email_log_id} not found"}

    # Update status to sending
    email_log.status = EmailLog.Status.SENDING
    email_log.retry_count = self.request.retries
    email_log.save(update_fields=["status", "retry_count"])

    message = email_log.email_log_message

    try:
        # Create the email message for this single recipient
        email = EmailMessage(
            subject=message.subject,
            body=message.body,
            from_email=message.from_email,
            to=[email_log.to_email] if email_log.recipient_type == "to" else [],
            cc=[email_log.to_email] if email_log.recipient_type == "cc" else [],
            bcc=[email_log.to_email] if email_log.recipient_type == "bcc" else [],
        )

        # Send using the actual SMTP backend (not EmailLogBackend to avoid recursion)
        email.connection = _get_smtp_connection()
        email.send(fail_silently=False)

        # Mark as sent
        email_log.status = EmailLog.Status.SENT
        email_log.sent_at = timezone.now()
        email_log.error_message = None
        email_log.save(update_fields=["status", "sent_at", "error_message"])

        return {"status": "sent", "email_log_id": email_log_id}

    except Exception as exc:
        # Update retry count on failure
        email_log.retry_count = self.request.retries
        email_log.error_message = str(exc)

        # Check if we've exhausted retries
        if self.request.retries >= self.max_retries:
            email_log.status = EmailLog.Status.FAILED
            email_log.save(update_fields=["status", "retry_count", "error_message"])
            return {
                "status": "failed",
                "email_log_id": email_log_id,
                "error": str(exc),
            }

        # Save current state before retry
        email_log.save(update_fields=["retry_count", "error_message"])

        # Re-raise to trigger retry
        raise


def _get_smtp_connection():
    """
    Get a connection to the actual SMTP backend.

    This bypasses EmailLogBackend to avoid infinite recursion.
    Uses EMAIL_ACTUAL_BACKEND setting if defined, otherwise falls back to SMTP.
    """
    from django.conf import settings
    from django.core.mail import get_connection

    backend_path = getattr(
        settings,
        "EMAIL_ACTUAL_BACKEND",
        "django.core.mail.backends.smtp.EmailBackend",
    )

    return get_connection(backend=backend_path)
