"""
app.py
FastAPI application for newsletter subscription management.
"""

from __future__ import annotations

import html
from contextlib import asynccontextmanager
from collections import defaultdict, deque
from time import monotonic

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

from config import FRONTEND_ORIGINS
from src.mailer import send_confirmation_email
from src.persistence import (
    cleanup_tokens,
    confirm_subscriber,
    create_confirm_link,
    init_db,
    unsubscribe_subscriber,
    upsert_pending_subscriber,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    cleanup_tokens()
    yield


app = FastAPI(title="OmniBrief API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class SubscribeRequest(BaseModel):
    email: EmailStr


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


RATE_LIMITS = {
    "subscribe_ip": (5, 600),
    "subscribe_email": (3, 3600),
    "confirm_ip": (20, 600),
    "unsubscribe_ip": (20, 600),
    "contact_ip": (3, 3600),
}
_rate_buckets = defaultdict(deque)


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _enforce_rate_limit(bucket: str, subject: str) -> None:
    limit, window_seconds = RATE_LIMITS[bucket]
    now = monotonic()
    key = f"{bucket}:{subject}"
    events = _rate_buckets[key]
    while events and now - events[0] > window_seconds:
        events.popleft()
    if len(events) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    events.append(now)


def _status_page(title: str, message: str) -> HTMLResponse:
    safe_title = html.escape(title)
    safe_message = html.escape(message)
    html_content = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{safe_title}</title>
      </head>
      <body style="margin:0;background:#f8fafc;font-family:Helvetica,Arial,sans-serif;color:#0f172a;">
        <div style="max-width:560px;margin:48px auto;padding:0 20px;">
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:32px;">
            <div style="font-size:30px;font-weight:800;letter-spacing:-0.8px;">OmniBrief.</div>
            <h1 style="font-size:24px;margin-top:24px;">{safe_title}</h1>
            <p style="font-size:16px;line-height:1.7;color:#334155;">{safe_message}</p>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)


def _action_page(title: str, message: str, action: str, button_label: str, token: str) -> HTMLResponse:
    safe_title = html.escape(title)
    safe_message = html.escape(message)
    html_content = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{safe_title}</title>
      </head>
      <body style="margin:0;background:#f8fafc;font-family:Helvetica,Arial,sans-serif;color:#0f172a;">
        <div style="max-width:560px;margin:48px auto;padding:0 20px;">
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:32px;">
            <div style="font-size:30px;font-weight:800;letter-spacing:-0.8px;">OmniBrief.</div>
            <h1 style="font-size:24px;margin-top:24px;">{safe_title}</h1>
            <p style="font-size:16px;line-height:1.7;color:#334155;">{safe_message}</p>
            <form method="post" action="{action}" style="margin-top:24px;">
              <input type="hidden" name="token" value="{token}" />
              <button type="submit" style="display:inline-block;background:#0f172a;color:#ffffff;padding:12px 20px;border-radius:8px;border:none;font-weight:700;cursor:pointer;">
                {html.escape(button_label)}
              </button>
            </form>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/subscribe")
async def subscribe(payload: SubscribeRequest, request: Request) -> dict:
    client_ip = _get_client_ip(request)
    _enforce_rate_limit("subscribe_ip", client_ip)
    _enforce_rate_limit("subscribe_email", payload.email.lower())
    subscriber = upsert_pending_subscriber(payload.email)
    if subscriber["status"] != "active":
        confirm_url = create_confirm_link(subscriber["id"])
        await send_confirmation_email(subscriber["email"], confirm_url)
    return {
        "message": "If this address can receive OmniBrief, a confirmation email has been sent."
    }


@app.post("/contact")
async def contact(payload: ContactRequest, request: Request) -> dict:
    client_ip = _get_client_ip(request)
    _enforce_rate_limit("contact_ip", client_ip)

    from config import ADMIN_EMAIL
    from src.mailer import _send_email

    safe_name = html.escape(payload.name)
    safe_email = html.escape(payload.email)
    safe_message = html.escape(payload.message)

    html_email = f"""
    <div style="font-family:Helvetica,Arial,sans-serif;background:#f8fafc;padding:48px 20px;color:#0f172a;">
        <div style="max-width:600px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:40px;shadow:0 4px 6px -1px rgb(0 0 0 / 0.1);">
            <div style="border-bottom:2px solid #f1f5f9;padding-bottom:24px;margin-bottom:32px;">
                <div style="font-size:24px;font-weight:800;letter-spacing:-0.02em;color:#0f172a;">OmniBrief.</div>
                <div style="font-size:14px;color:#64748b;margin-top:4px;">Inquiry from Direct Contact Form</div>
            </div>
            
            <div style="margin-bottom:32px;">
                <label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;tracking:0.1em;color:#94a3b8;margin-bottom:8px;">Sender Details</label>
                <div style="font-size:16px;color:#0f172a;background:#f8fafc;padding:16px;border-radius:12px;border:1px solid #f1f5f9;">
                    <strong>{safe_name}</strong><br/>
                    <a href="mailto:{safe_email}" style="color:#3b82f6;text-decoration:none;">{safe_email}</a>
                </div>
            </div>
            
            <div>
                <label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;tracking:0.1em;color:#94a3b8;margin-bottom:8px;">Message Content</label>
                <div style="font-size:16px;line-height:1.6;color:#334155;background:#f8fafc;padding:20px;border-radius:12px;border:1px solid #f1f5f9;white-space:pre-wrap;">{safe_message}</div>
            </div>
            
            <div style="margin-top:40px;padding-top:24px;border-top:1px solid #f1f5f9;font-size:12px;color:#94a3b8;text-align:center;">
                This message was sent from the OmniBrief landing page contact form.
            </div>
        </div>
    </div>
    """

    try:
        await _send_email(
            to_email=ADMIN_EMAIL,
            subject=f"Inquiry: {payload.name} via OmniBrief",
            html_content=html_email,
        )
        return {"message": "Message sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send message.")


@app.get("/confirm", response_class=HTMLResponse)
async def confirm_page(token: str) -> HTMLResponse:
    return _action_page(
        "Confirm Subscription",
        "Click below to confirm your OmniBrief subscription and start receiving the daily briefing.",
        "/confirm",
        "Confirm Subscription",
        token,
    )


@app.post("/confirm", response_class=HTMLResponse)
async def confirm(token: str = Form(...), request: Request = None) -> HTMLResponse:
    _enforce_rate_limit("confirm_ip", _get_client_ip(request))
    subscriber = confirm_subscriber(token)
    if not subscriber:
        return _status_page(
            "Confirmation Link Invalid",
            "This confirmation link is invalid, expired, or has already been used.",
        )
    return _status_page(
        "Subscription Confirmed",
        f"{subscriber['email']} is now subscribed to OmniBrief.",
    )


@app.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe_page(token: str) -> HTMLResponse:
    return _action_page(
        "Confirm Unsubscribe",
        "Click below if you want to stop receiving the OmniBrief daily briefing.",
        "/unsubscribe",
        "Unsubscribe",
        token,
    )


@app.post("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe(token: str = Form(...), request: Request = None) -> HTMLResponse:
    _enforce_rate_limit("unsubscribe_ip", _get_client_ip(request))
    subscriber = unsubscribe_subscriber(token)
    if not subscriber:
        return _status_page(
            "Unsubscribe Link Invalid",
            "This unsubscribe link is invalid, expired, or has already been used.",
        )
    return _status_page(
        "You Have Been Unsubscribed",
        f"{subscriber['email']} will no longer receive OmniBrief.",
    )
