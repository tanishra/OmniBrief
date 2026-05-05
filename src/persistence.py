"""
src/persistence.py
PostgreSQL-backed persistence for digest history, subscribers, tokens, and delivery logs.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import quote

import psycopg
from psycopg.rows import dict_row

from config import (
    APP_BASE_URL,
    BOOTSTRAP_RECIPIENT_AS_SUBSCRIBER,
    DATABASE_URL,
    NEWSLETTER_TOKEN_SECRET,
    RECIPIENT_EMAIL,
    SUBSCRIBE_TOKEN_TTL_HOURS,
    UNSUBSCRIBE_TOKEN_TTL_DAYS,
)


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


def init_db() -> None:
    """Initializes the PostgreSQL schema."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_items (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    section TEXT,
                    sent_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS subscribers (
                    id BIGSERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL CHECK (status IN ('pending', 'active', 'unsubscribed')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    confirmed_at TIMESTAMPTZ,
                    unsubscribed_at TIMESTAMPTZ
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriber_tokens (
                    id BIGSERIAL PRIMARY KEY,
                    subscriber_id BIGINT NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
                    purpose TEXT NOT NULL CHECK (purpose IN ('confirm', 'unsubscribe')),
                    token_hash TEXT NOT NULL UNIQUE,
                    expires_at TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    used_at TIMESTAMPTZ
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS delivery_logs (
                    id BIGSERIAL PRIMARY KEY,
                    subscriber_id BIGINT NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
                    campaign_key TEXT NOT NULL,
                    resend_message_id TEXT,
                    status TEXT NOT NULL CHECK (status IN ('sent', 'failed')),
                    error TEXT,
                    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (subscriber_id, campaign_key)
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_subscribers_status
                ON subscribers (status)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tokens_lookup
                ON subscriber_tokens (purpose, token_hash, used_at, expires_at)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_delivery_campaign
                ON delivery_logs (campaign_key, status)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limits (
                    key TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rate_limits_key_timestamp
                ON rate_limits (key, timestamp)
                """
            )

        conn.commit()


def load_history() -> set[str]:
    """Loads sent URLs into a set for fast lookup."""
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT url FROM sent_items")
            return {row[0] for row in cur.fetchall()}


def is_duplicate(url: str, history_set: Optional[set[str]] = None) -> bool:
    """Checks if a URL has already been sent."""
    if not url:
        return False
    if history_set is not None and url in history_set:
        return True
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM sent_items WHERE url = %s", (url,))
            return cur.fetchone() is not None


def mark_sent(url: str, title: str = "", source: str = "", section: str = "") -> None:
    """Saves a digest item to the global sent history."""
    if not url:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
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
        conn.commit()


def cleanup_history(days: int = 14) -> None:
    """Removes old sent history entries."""
    cutoff = _utcnow() - timedelta(days=days)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sent_items WHERE sent_at < %s", (cutoff,))
        conn.commit()


def cleanup_tokens(retention_days: int = 7) -> None:
    """Removes expired or used tokens after a short retention period."""
    cutoff = _utcnow() - timedelta(days=retention_days)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM subscriber_tokens
                WHERE (used_at IS NOT NULL AND used_at < %s)
                   OR (expires_at < %s)
                """,
                (cutoff, cutoff),
            )
        conn.commit()


def ensure_default_subscriber() -> None:
    """Bootstraps the legacy recipient as an active subscriber for backwards compatibility."""
    if not BOOTSTRAP_RECIPIENT_AS_SUBSCRIBER or not RECIPIENT_EMAIL:
        return
    email = _normalize_email(RECIPIENT_EMAIL)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO subscribers (email, status, confirmed_at)
                VALUES (%s, 'active', NOW())
                ON CONFLICT (email) DO NOTHING
                """,
                (email,),
            )
        conn.commit()


def _build_action_url(path: str, token: str) -> str:
    base = APP_BASE_URL.rstrip("/")
    return f"{base}{path}?token={quote(token)}"


def _issue_token(subscriber_id: int, purpose: str, ttl: timedelta) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = _utcnow() + ttl
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO subscriber_tokens (subscriber_id, purpose, token_hash, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (subscriber_id, purpose, token_hash, expires_at),
            )
        conn.commit()
    return raw_token


def create_confirm_link(subscriber_id: int) -> str:
    token = _issue_token(subscriber_id, "confirm", timedelta(hours=SUBSCRIBE_TOKEN_TTL_HOURS))
    return _build_action_url("/confirm", token)


def create_unsubscribe_link(subscriber_id: int) -> str:
    token = _issue_token(subscriber_id, "unsubscribe", timedelta(days=UNSUBSCRIBE_TOKEN_TTL_DAYS))
    return _build_action_url("/unsubscribe", token)


def upsert_pending_subscriber(email: str) -> Dict[str, Any]:
    """Creates or refreshes a pending subscriber while keeping active subscribers active."""
    normalized = _normalize_email(email)
    with get_conn(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
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
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def list_active_subscribers_for_campaign(campaign_key: str) -> List[Dict[str, Any]]:
    """Returns active subscribers who have not yet received the campaign."""
    with get_conn(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
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
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def record_delivery(
    subscriber_id: int,
    campaign_key: str,
    *,
    status: str,
    resend_message_id: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
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
        conn.commit()


def _consume_token(raw_token: str, purpose: str) -> Optional[Dict[str, Any]]:
    token_hash = _hash_token(raw_token)
    now = _utcnow()
    with get_conn(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
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
            row = cur.fetchone()
            if not row:
                return None
            if row["used_at"] is not None or row["expires_at"] < now:
                return None

            cur.execute(
                "UPDATE subscriber_tokens SET used_at = %s WHERE id = %s",
                (now, row["token_id"]),
            )
            if purpose == "confirm":
                cur.execute(
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
                cur.execute(
                    """
                    UPDATE subscribers
                    SET status = 'unsubscribed',
                        unsubscribed_at = %s
                    WHERE id = %s
                    RETURNING id, email, status
                    """,
                    (now, row["subscriber_id"]),
                )
            updated = cur.fetchone()
        conn.commit()
    return dict(updated) if updated else None


def confirm_subscriber(raw_token: str) -> Optional[Dict[str, Any]]:
    return _consume_token(raw_token, "confirm")


def unsubscribe_subscriber(raw_token: str) -> Optional[Dict[str, Any]]:
    return _consume_token(raw_token, "unsubscribe")


def enforce_rate_limit(bucket: str, subject: str, limit: int, window_seconds: int) -> bool:
    """
    Returns True if allowed, False if rate limited.
    """
    key = f"{bucket}:{subject}"
    cutoff = _utcnow() - timedelta(seconds=window_seconds)

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Clean up old entries occasionally (could be a background job, but this is simple)
            cur.execute("DELETE FROM rate_limits WHERE timestamp < %s", (cutoff,))

            # Count recent requests
            cur.execute("SELECT COUNT(*) FROM rate_limits WHERE key = %s AND timestamp >= %s", (key, cutoff))
            count = cur.fetchone()[0]

            if count >= limit:
                conn.commit()
                return False

            # Log new request
            cur.execute("INSERT INTO rate_limits (key, timestamp) VALUES (%s, %s)", (key, _utcnow()))
            conn.commit()
            return True
