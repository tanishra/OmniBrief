"""
src/mailer.py
Resend email delivery for confirmation, digest, and alert emails.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import ADMIN_EMAIL, RESEND_API_KEY, SENDER_EMAIL, SENDER_NAME

RESEND_SEND_URL = "https://api.resend.com/emails"


async def _send_email(
    *,
    to_email: str,
    subject: str,
    html_content: str,
) -> Dict[str, Any]:
    payload = {
        "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            RESEND_SEND_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code not in (200, 201):
        print(f"❌ Resend error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    return resp.json()


def build_digest_subject() -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    return f"⚡ OmniBrief — {date_str}"


async def send_digest(html_content: str, recipient_email: str) -> Dict[str, Any]:
    """Sends the HTML digest email to a single subscriber."""
    data = await _send_email(
        to_email=recipient_email,
        subject=build_digest_subject(),
        html_content=html_content,
    )
    print(f"✅ Email sent to {recipient_email}. Resend ID: {data.get('id')}")
    return data


async def send_confirmation_email(recipient_email: str, confirm_url: str) -> Dict[str, Any]:
    html = f"""
    <div style="font-family:Helvetica,Arial,sans-serif;background:#f8fafc;padding:32px;color:#0f172a;">
        <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:32px;">
            <div style="font-size:28px;font-weight:800;letter-spacing:-0.5px;">OmniBrief.</div>
            <p style="margin-top:20px;font-size:16px;line-height:1.7;color:#334155;">
                Confirm your subscription to start receiving the daily OmniBrief digest.
            </p>
            <a href="{confirm_url}" style="display:inline-block;margin-top:16px;background:#0f172a;color:#ffffff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:700;">
                Confirm Subscription
            </a>
            <p style="margin-top:20px;font-size:13px;line-height:1.6;color:#64748b;">
                If you did not request this, you can ignore this email. This link expires automatically.
            </p>
        </div>
    </div>
    """
    data = await _send_email(
        to_email=recipient_email,
        subject="Confirm your OmniBrief subscription",
        html_content=html,
    )
    print(f"✅ Confirmation email sent to {recipient_email}. Resend ID: {data.get('id')}")
    return data


async def send_error_alert(error_message: str) -> None:
    """Sends a plain-text error alert if the main digest run fails."""
    date_str = datetime.now().strftime("%B %d, %Y")
    subject = f"⚠️ OmniBrief FAILED — {date_str}"

    html = f"""
    <div style="font-family:monospace;background:#111;color:#ef4444;padding:24px;border-radius:8px;">
        <h2 style="color:#ef4444">⚠️ OmniBrief Run Failed</h2>
        <p style="color:#94a3b8;margin-top:12px;">Date: {date_str}</p>
        <pre style="background:#000;padding:16px;border-radius:6px;margin-top:16px;
                    color:#fca5a5;font-size:13px;overflow:auto;">{error_message}</pre>
    </div>
    """

    try:
        await _send_email(
            to_email=ADMIN_EMAIL,
            subject=subject,
            html_content=html,
        )
        print(f"⚠️  Error alert sent to {ADMIN_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send error alert: {e}")


if __name__ == "__main__":
    test_html = """
    <div style="font-family:sans-serif;background:#0a0a0f;color:#e2e8f0;padding:40px;border-radius:12px;">
        <h1 style="color:#a5b4fc">⚡ OmniBrief Test Email</h1>
    </div>
    """
    asyncio.run(send_digest(test_html, ADMIN_EMAIL))
