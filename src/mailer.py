"""
src/mailer.py
Sends the rendered HTML digest via Resend's API.
"""

import httpx
import asyncio
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import RESEND_API_KEY, RECIPIENT_EMAIL, SENDER_EMAIL, SENDER_NAME

RESEND_SEND_URL = "https://api.resend.com/emails"


async def send_digest(html_content: str) -> dict:
    """Sends the HTML digest email via Resend."""
    date_str = datetime.now().strftime("%B %d, %Y")
    subject  = f"⚡ OmniBrief — {date_str}"

    payload = {
        "from":    f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to":      [RECIPIENT_EMAIL],
        "subject": subject,
        "html":    html_content,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            RESEND_SEND_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
        )

        if resp.status_code not in (200, 201):
            print(f"❌ Resend error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        data = resp.json()
        print(f"✅ Email sent! Resend ID: {data.get('id')}")
        return data


async def send_error_alert(error_message: str) -> None:
    """Sends a plain-text error alert if the main digest run fails."""
    date_str = datetime.now().strftime("%B %d, %Y")
    subject  = f"⚠️ OmniBrief FAILED — {date_str}"

    html = f"""
    <div style="font-family:monospace;background:#111;color:#ef4444;padding:24px;border-radius:8px;">
        <h2 style="color:#ef4444">⚠️ OmniBrief Run Failed</h2>
        <p style="color:#94a3b8;margin-top:12px;">Date: {date_str}</p>
        <pre style="background:#000;padding:16px;border-radius:6px;margin-top:16px;
                    color:#fca5a5;font-size:13px;overflow:auto;">{error_message}</pre>
    </div>
    """

    payload = {
        "from":    f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to":      [RECIPIENT_EMAIL],
        "subject": subject,
        "html":    html,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                RESEND_SEND_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type":  "application/json",
                },
            )
            resp.raise_for_status()
            print(f"⚠️  Error alert sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send error alert: {e}")


if __name__ == "__main__":
    test_html = """
    <div style="font-family:sans-serif;background:#0a0a0f;color:#e2e8f0;padding:40px;border-radius:12px;">
        <h1 style="color:#a5b4fc">⚡ OmniBrief Test Email</h1>
    </div>
    """
    asyncio.run(send_digest(test_html))
