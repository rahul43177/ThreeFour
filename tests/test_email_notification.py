#!/usr/bin/env python3
"""
Test script for email notifications.
Run this to verify email configuration is working correctly.
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_email_notification():
    """Test the email notification system."""
    print("Testing email notification...")

    # Import the email notifier
    try:
        from app.email_notifier import send_email_notification, can_send_email_notifications
    except Exception as e:
        print(f"Error importing email notifier: {e}")
        return False

    # Check if email is configured
    if not can_send_email_notifications():
        print("❌ Email notifications not configured properly.")
        print("Check your .env file for these variables:")
        print("  - EMAIL_ADDRESS")
        print("  - EMAIL_PASSWORD")
        print("  - EMAIL_TO")
        return False

    # Send test email
    print("Attempting to send test email...")
    success = send_email_notification(
        "WiFi Tracker Test",
        "This is a test notification from your WiFi tracking timer.\n\nIf you received this, email notifications are working!"
    )

    if success:
        print("✅ Test email sent successfully!")
        print("Check your inbox for the test message.")
        return True
    else:
        print("❌ Failed to send test email.")
        print("Check the logs for error details.")
        return False

if __name__ == "__main__":
    test_email_notification()
