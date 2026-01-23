"""Email service using Forward Email API."""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailResult:
    """Result of sending an email."""

    success: bool
    message_id: str | None = None
    error: str | None = None


async def send_magic_link_email(to_email: str, magic_link: str) -> EmailResult:
    """
    Send a magic link email using Forward Email API.

    Args:
        to_email: Recipient email address
        magic_link: Full magic link URL

    Returns:
        EmailResult with success status
    """
    subject = "Sign in to Class Portal"
    html_body = f"""
    <html>
    <body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2>Sign in to Class Portal</h2>
        <p>Click the link below to sign in. This link expires in {settings.magic_link_ttl_minutes} minutes.</p>
        <p style="margin: 24px 0;">
            <a href="{magic_link}"
               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                Sign In
            </a>
        </p>
        <p style="color: #666; font-size: 14px;">
            Or copy this link: <br>
            <code style="word-break: break-all;">{magic_link}</code>
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="color: #999; font-size: 12px;">
            If you didn't request this link, you can safely ignore this email.
        </p>
    </body>
    </html>
    """

    text_body = f"""
Sign in to Class Portal

Click the link below to sign in. This link expires in {settings.magic_link_ttl_minutes} minutes.

{magic_link}

If you didn't request this link, you can safely ignore this email.
    """

    return await send_email(
        to=to_email,
        subject=subject,
        html=html_body,
        text=text_body,
    )


async def send_email(
    to: str,
    subject: str,
    html: str | None = None,
    text: str | None = None,
) -> EmailResult:
    """
    Send an email using Forward Email API.

    Args:
        to: Recipient email address
        subject: Email subject
        html: HTML body (optional)
        text: Plain text body (optional)

    Returns:
        EmailResult with success status
    """
    if not settings.forwardemail_user or not settings.forwardemail_pass:
        logger.error("Forward Email credentials not configured")
        return EmailResult(success=False, error="Email not configured")

    payload = {
        "from": settings.forwardemail_user,
        "to": to,
        "subject": subject,
    }

    if html:
        payload["html"] = html
    if text:
        payload["text"] = text

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.forwardemail_api_url,
                auth=(settings.forwardemail_user, settings.forwardemail_pass),
                json=payload,
                timeout=30.0,
            )

            if response.status_code in (200, 201, 202):
                data = response.json()
                message_id = data.get("id") or data.get("message_id")
                logger.info("Email sent to %s (id: %s)", to, message_id)
                return EmailResult(success=True, message_id=message_id)

            error_msg = f"API returned {response.status_code}: {response.text}"
            logger.error("Failed to send email to %s: %s", to, error_msg)
            return EmailResult(success=False, error=error_msg)

    except httpx.TimeoutException:
        logger.error("Timeout sending email to %s", to)
        return EmailResult(success=False, error="Request timeout")
    except httpx.RequestError as e:
        logger.error("Request error sending email to %s: %s", to, e)
        return EmailResult(success=False, error=str(e))
    except Exception as e:
        logger.exception("Unexpected error sending email to %s", to)
        return EmailResult(success=False, error=str(e))
