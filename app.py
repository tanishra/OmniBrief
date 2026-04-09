"""
app.py
FastAPI application for newsletter subscription management.
"""

from __future__ import annotations

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


RATE_LIMITS = {
    "subscribe_ip": (5, 600),
    "subscribe_email": (3, 3600),
    "confirm_ip": (20, 600),
    "unsubscribe_ip": (20, 600),
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
    html = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
      </head>
      <body style="margin:0;background:#f8fafc;font-family:Helvetica,Arial,sans-serif;color:#0f172a;">
        <div style="max-width:560px;margin:48px auto;padding:0 20px;">
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:32px;">
            <div style="font-size:30px;font-weight:800;letter-spacing:-0.8px;">OmniBrief.</div>
            <h1 style="font-size:24px;margin-top:24px;">{title}</h1>
            <p style="font-size:16px;line-height:1.7;color:#334155;">{message}</p>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


def _action_page(title: str, message: str, action: str, button_label: str, token: str) -> HTMLResponse:
    html = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
      </head>
      <body style="margin:0;background:#f8fafc;font-family:Helvetica,Arial,sans-serif;color:#0f172a;">
        <div style="max-width:560px;margin:48px auto;padding:0 20px;">
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:32px;">
            <div style="font-size:30px;font-weight:800;letter-spacing:-0.8px;">OmniBrief.</div>
            <h1 style="font-size:24px;margin-top:24px;">{title}</h1>
            <p style="font-size:16px;line-height:1.7;color:#334155;">{message}</p>
            <form method="post" action="{action}" style="margin-top:24px;">
              <input type="hidden" name="token" value="{token}" />
              <button type="submit" style="display:inline-block;background:#0f172a;color:#ffffff;padding:12px 20px;border-radius:8px;border:none;font-weight:700;cursor:pointer;">
                {button_label}
              </button>
            </form>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


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
