"""
Email notification module.
Sends email notifications when 4-hour work period is complete.

Uses Python's built-in smtplib and email libraries for sending emails.
Supports Gmail, Outlook, and other SMTP providers.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def can_send_email_notifications() -> bool:
    """
    Check if email notifications are configured.

    Returns:
        True if required email settings are configured, False otherwise.
    """
    return bool(
        settings.email_address.strip()
        and settings.email_password.strip()
        and settings.email_to.strip()
    )


def send_email_notification(
    title: str,
    message: str,
    html_message: Optional[str] = None,
) -> bool:
    """
    Send an email notification when timer completes.

    Args:
        title: Email subject line
        message: Plain-text email body content
        html_message: Optional HTML email body (sent with plain-text fallback)

    Returns:
        True if email was sent successfully, False otherwise.
    """
    # Skip if not configured
    if not can_send_email_notifications():
        logger.debug("Email notifications not configured; skipping")
        return False

    try:
        email_address = settings.email_address.strip()
        email_password = settings.email_password.strip()
        email_to = settings.email_to.strip()
        smtp_server = settings.smtp_server.strip() or "smtp.gmail.com"
        smtp_port = int(settings.smtp_port)

        # Create message
        msg = MIMEMultipart("alternative")
        msg['From'] = email_address
        msg['To'] = email_to
        msg['Subject'] = title

        # Plain-text fallback is always attached first for compatibility.
        msg.attach(MIMEText(message, 'plain'))
        if html_message:
            msg.attach(MIMEText(html_message, 'html'))

        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.starttls()  # Enable TLS encryption
            server.login(email_address, email_password)

            # Send email
            text = msg.as_string()
            server.sendmail(email_address, email_to, text)

        logger.info("Email notification sent: %s — %s", title, message)
        return True

    except Exception as e:
        logger.warning("Failed to send email notification: %s", e)
        return False
