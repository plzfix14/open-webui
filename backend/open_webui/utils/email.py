import logging
import requests
from typing import Optional

from open_webui.env import (
    MAILGUN_API_KEY,
    MAILGUN_DOMAIN,
    MAILGUN_FROM_EMAIL,
    MAILGUN_API_URL,
    WEBUI_NAME,
)

log = logging.getLogger(__name__)


def is_email_configured() -> bool:
    """Check if Mailgun is properly configured"""
    return bool(MAILGUN_API_KEY and MAILGUN_DOMAIN and MAILGUN_FROM_EMAIL)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> bool:
    """
    Send an email using Mailgun API.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional, derived from html if not provided)

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not is_email_configured():
        log.error("Mailgun is not configured. Please set MAILGUN_API_KEY, MAILGUN_DOMAIN, and MAILGUN_FROM_EMAIL.")
        return False

    try:
        response = requests.post(
            f"{MAILGUN_API_URL}/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": html_content,
                "text": text_content or html_content,
            },
            timeout=30,
        )

        if response.status_code == 200:
            log.info(f"Email sent successfully to {to_email}")
            return True
        else:
            log.error(f"Failed to send email: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        log.error(f"Error sending email: {e}")
        return False


def send_password_reset_email(
    to_email: str,
    reset_link: str,
    user_name: Optional[str] = None,
    webui_url: Optional[str] = None,
) -> bool:
    """
    Send a password reset email.

    Args:
        to_email: Recipient email address
        reset_link: The password reset link
        user_name: User's display name (optional)
        webui_url: The base URL of the WebUI (optional)

    Returns:
        True if email was sent successfully, False otherwise
    """
    app_name = WEBUI_NAME or "Open WebUI"
    display_name = user_name or "User"

    subject = f"Password Reset Request - {app_name}"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 8px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #1a1a1a; margin-bottom: 20px; font-size: 24px;">Password Reset Request</h1>
        <p style="margin-bottom: 15px;">Hello {display_name},</p>
        <p style="margin-bottom: 15px;">We received a request to reset the password for your {app_name} account associated with this email address.</p>
        <p style="margin-bottom: 25px;">Click the button below to reset your password:</p>
        <div style="text-align: center; margin-bottom: 25px;">
            <a href="{reset_link}" style="display: inline-block; background-color: #000; color: #fff; text-decoration: none; padding: 12px 30px; border-radius: 6px; font-weight: 500;">Reset Password</a>
        </div>
        <p style="margin-bottom: 15px; font-size: 14px; color: #666;">If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="margin-bottom: 15px; font-size: 14px; word-break: break-all;"><a href="{reset_link}" style="color: #0066cc;">{reset_link}</a></p>
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 25px 0;">
        <p style="font-size: 13px; color: #888; margin-bottom: 10px;">This link will expire in 1 hour for security reasons.</p>
        <p style="font-size: 13px; color: #888; margin-bottom: 0;">If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
    </div>
    <div style="text-align: center; font-size: 12px; color: #999;">
        <p>&copy; {app_name}. All rights reserved.</p>
    </div>
</body>
</html>
"""

    text_content = f"""
Password Reset Request

Hello {display_name},

We received a request to reset the password for your {app_name} account associated with this email address.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

© {app_name}. All rights reserved.
"""

    return send_email(to_email, subject, html_content, text_content)
