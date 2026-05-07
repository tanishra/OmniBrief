from __future__ import annotations
"""
src/persistence.py
PostgreSQL-backed persistence for digest history, subscribers, tokens, and delivery logs.
"""

from src.logger import logger

import hashlib
import hmac
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import quote

import psycopg
from psycopg.rows import dict_row
from typing import AsyncGenerator

from config import (
    APP_BASE_URL,
    BOOTSTRAP_RECIPIENT_AS_SUBSCRIBER,
    DATABASE_URL,
    NEWSLETTER_TOKEN_SECRET,
    RECIPIENT_EMAIL,
    SUBSCRIBE_TOKEN_TTL_HOURS,
    UNSUBSCRIBE_TOKEN_TTL_DAYS,
)


from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager

_async_pool: Optional[AsyncConnectionPool] = None

async def init_async_pool():
    global _async_pool
    if _async_pool is None:
        _async_pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=10,
            timeout=30.0,
            max_idle=300
        )
        await _async_pool.open()

async def close_async_pool():
    global _async_pool
    if _async_pool is not None:
        await _async_pool.close()
        _async_pool = None

@asynccontextmanager
async def get_async_conn():
    if _async_pool is None:
        await init_async_pool()
    async with _async_pool.connection() as conn:
        yield conn

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_token(raw_token: str) -> str:
    if not NEWSLETTER_TOKEN_SECRET:
        raise EnvironmentError("Missing required environment variable: NEWSLETTER_TOKEN_SECRET")
    return hmac.new(
        NEWSLETTER_TOKEN_SECRET.encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


@contextmanager
def get_conn(*, row_factory=None) -> Iterator[psycopg.Connection]:
    if not DATABASE_URL:
        raise EnvironmentError("Missing required environment variable: DATABASE_URL")
    conn = psycopg.connect(DATABASE_URL, row_factory=row_factory)
    try:
        yield conn
    finally:
        conn.close()





async def load_history() -> set[str]:
    """Loads sent URLs into a set for fast lookup."""
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT url FROM sent_items")
            return {row[0] for row in await cur.fetchall()}


async def is_duplicate(url: str, history_set: Optional[set[str]] = None) -> bool:
    """Checks if a URL has already been sent."""
    if not url:
        return False
    if history_set is not None and url in history_set:
        return True
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1 FROM sent_items WHERE url = %s", (url,))
            return await cur.fetchone() is not None


async def mark_sent(url: str, title: str = "", source: str = "", section: str = "") -> None:
    """Saves a digest item to the global sent history."""
    if not url:
        return
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO sent_items (url, title, source, section)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE
                SET title = EXCLUDED.title,
                    source = EXCLUDED.source,
                    section = EXCLUDED.section
                """,
                (url, title, source, section),
            )
        await conn.commit()


async def cleanup_history(days: int = 14) -> None:
    """Removes old sent history entries."""
    cutoff = _utcnow() - timedelta(days=days)
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM sent_items WHERE sent_at < %s", (cutoff,))
        await conn.commit()


async def cleanup_tokens(retention_days: int = 7) -> None:
    """Removes expired or used tokens after a short retention period."""
    cutoff = _utcnow() - timedelta(days=retention_days)
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM subscriber_tokens
                WHERE (used_at IS NOT NULL AND used_at < %s)
                   OR (expires_at < %s)
                """,
                (cutoff, cutoff),
            )
        await conn.commit()


async def ensure_default_subscriber() -> None:
    """Bootstraps the legacy recipient as an active subscriber for backwards compatibility."""
    if not BOOTSTRAP_RECIPIENT_AS_SUBSCRIBER or not RECIPIENT_EMAIL:
        return
    email = _normalize_email(RECIPIENT_EMAIL)
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO subscribers (email, status, confirmed_at)
                VALUES (%s, 'active', NOW())
                ON CONFLICT (email) DO NOTHING
                """,
                (email,),
            )
        await conn.commit()


def _build_action_url(path: str, token: str) -> str:
    base = APP_BASE_URL.rstrip("/")
    return f"{base}{path}?token={quote(token)}"


async def _issue_token(subscriber_id: int, purpose: str, ttl: timedelta) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = _utcnow() + ttl
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO subscriber_tokens (subscriber_id, purpose, token_hash, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (subscriber_id, purpose, token_hash, expires_at),
            )
        await conn.commit()
    return raw_token


async def create_confirm_link(subscriber_id: int) -> str:
    token = await _issue_token(subscriber_id, "confirm", timedelta(hours=SUBSCRIBE_TOKEN_TTL_HOURS))
    return _build_action_url("/confirm", token)


async def create_unsubscribe_link(subscriber_id: int) -> str:
    token = await _issue_token(subscriber_id, "unsubscribe", timedelta(days=UNSUBSCRIBE_TOKEN_TTL_DAYS))
    return _build_action_url("/unsubscribe", token)


async def upsert_pending_subscriber(email: str) -> Dict[str, Any]:
    """Creates or refreshes a pending subscriber while keeping active subscribers active."""
    normalized = _normalize_email(email)
    async with get_async_conn() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO subscribers (email, status)
                VALUES (%s, 'pending')
                ON CONFLICT (email) DO UPDATE
                SET status = CASE
                        WHEN subscribers.status = 'active' THEN subscribers.status
                        ELSE 'pending'
                    END,
                    unsubscribed_at = CASE
                        WHEN subscribers.status = 'active' THEN subscribers.unsubscribed_at
                        ELSE NULL
                    END
                RETURNING id, email, status, confirmed_at, unsubscribed_at
                """,
                (normalized,),
            )
            row = await cur.fetchone()
        await conn.commit()
    return dict(row)


async def list_active_subscribers_for_campaign(campaign_key: str) -> List[Dict[str, Any]]:
    """Returns active subscribers who have not yet received the campaign."""
    async with get_async_conn() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT s.id, s.email
                FROM subscribers AS s
                WHERE s.status = 'active'
                  AND NOT EXISTS (
                    SELECT 1
                    FROM delivery_logs AS d
                    WHERE d.subscriber_id = s.id
                      AND d.campaign_key = %s
                      AND d.status = 'sent'
                  )
                ORDER BY s.created_at ASC
                """,
                (campaign_key,),
            )
            rows = await cur.fetchall()
    return [dict(row) for row in rows]


async def record_delivery(
    subscriber_id: int,
    campaign_key: str,
    *,
    status: str,
    resend_message_id: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO delivery_logs (subscriber_id, campaign_key, resend_message_id, status, error)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (subscriber_id, campaign_key) DO UPDATE
                SET resend_message_id = EXCLUDED.resend_message_id,
                    status = EXCLUDED.status,
                    error = EXCLUDED.error,
                    sent_at = NOW()
                """,
                (subscriber_id, campaign_key, resend_message_id, status, error),
            )
        await conn.commit()


async def _consume_token(raw_token: str, purpose: str) -> Optional[Dict[str, Any]]:
    token_hash = _hash_token(raw_token)
    now = _utcnow()
    async with get_async_conn() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT t.id AS token_id, t.subscriber_id, s.email, s.status, t.expires_at, t.used_at
                FROM subscriber_tokens AS t
                JOIN subscribers AS s ON s.id = t.subscriber_id
                WHERE t.purpose = %s
                  AND t.token_hash = %s
                LIMIT 1
                """,
                (purpose, token_hash),
            )
            row = await cur.fetchone()
            if not row:
                return None
            if row["used_at"] is not None or row["expires_at"] < now:
                return None

            await cur.execute(
                "UPDATE subscriber_tokens SET used_at = %s WHERE id = %s",
                (now, row["token_id"]),
            )
            if purpose == "confirm":
                await cur.execute(
                    """
                    UPDATE subscribers
                    SET status = 'active',
                        confirmed_at = COALESCE(confirmed_at, %s),
                        unsubscribed_at = NULL
                    WHERE id = %s
                    RETURNING id, email, status
                    """,
                    (now, row["subscriber_id"]),
                )
            else:
                await cur.execute(
                    """
                    UPDATE subscribers
                    SET status = 'unsubscribed',
                        unsubscribed_at = %s
                    WHERE id = %s
                    RETURNING id, email, status
                    """,
                    (now, row["subscriber_id"]),
                )
            updated = await cur.fetchone()
        await conn.commit()
    return dict(updated) if updated else None


async def confirm_subscriber(raw_token: str) -> Optional[Dict[str, Any]]:
    return await _consume_token(raw_token, "confirm")


async def unsubscribe_subscriber(raw_token: str) -> Optional[Dict[str, Any]]:
    return await _consume_token(raw_token, "unsubscribe")


async def enforce_rate_limit(bucket: str, subject: str, limit: int, window_seconds: int) -> bool:
    """
    Returns True if allowed, False if rate limited.
    """
    key = f"{bucket}:{subject}"
    cutoff = _utcnow() - timedelta(seconds=window_seconds)

    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            # Clean up old entries for THIS key to save space over time
            await cur.execute("DELETE FROM rate_limits WHERE key = %s AND timestamp < %s", (key, cutoff))

            # Count recent requests
            await cur.execute("SELECT COUNT(*) FROM rate_limits WHERE key = %s AND timestamp >= %s", (key, cutoff))
            count = await cur.fetchone()[0]

            if count >= limit:
                await conn.commit()
                return False

            # Log new request
            await cur.execute("INSERT INTO rate_limits (key, timestamp) VALUES (%s, %s)", (key, _utcnow()))
            await conn.commit()
            return True

async def cleanup_rate_limits(days: int = 2) -> None:
    """Prunes old rate limit data."""
    cutoff = _utcnow() - timedelta(days=days)
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM rate_limits WHERE timestamp < %s", (cutoff,))
        await conn.commit()


async def archive_newsletter(campaign_key: str, html_content: str) -> None:
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO newsletter_archives (campaign_key, html_content)
                VALUES (%s, %s)
                ON CONFLICT (campaign_key) DO NOTHING
                """,
                (campaign_key, html_content)
            )
        await conn.commit()

async def record_feedback(campaign_key: str, subscriber_email: str, vote: str) -> None:
    async with get_async_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO campaign_feedback (campaign_key, subscriber_email, vote)
                VALUES (%s, %s, %s)
                ON CONFLICT (campaign_key, subscriber_email) DO UPDATE
                SET vote = EXCLUDED.vote
                """,
                (campaign_key, subscriber_email, vote)
            )
        await conn.commit()
