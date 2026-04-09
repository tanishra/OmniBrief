"""
app.py
FastAPI application for newsletter subscription management.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

from config import FRONTEND_ORIGINS
from src.mailer import send_confirmation_email
from src.persistence import (
    confirm_subscriber,
    create_confirm_link,
    init_db,
    unsubscribe_subscriber,
    upsert_pending_subscriber,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
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


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/subscribe")
async def subscribe(payload: SubscribeRequest) -> dict:
    subscriber = upsert_pending_subscriber(payload.email)
    if subscriber["status"] != "active":
        confirm_url = create_confirm_link(subscriber["id"])
        await send_confirmation_email(subscriber["email"], confirm_url)
    return {
        "message": "If this address can receive OmniBrief, a confirmation email has been sent."
    }


@app.get("/confirm", response_class=HTMLResponse)
async def confirm(token: str) -> HTMLResponse:
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
async def unsubscribe(token: str) -> HTMLResponse:
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