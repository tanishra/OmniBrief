"""initial

Revision ID: 001_initial
Revises:
Create Date: 2024-05-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'active', 'unsubscribed')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        confirmed_at TIMESTAMPTZ,
        unsubscribed_at TIMESTAMPTZ
    );

    CREATE TABLE IF NOT EXISTS subscriber_tokens (
        id SERIAL PRIMARY KEY,
        subscriber_id BIGINT NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
        purpose TEXT NOT NULL,
        token_hash TEXT NOT NULL,
        expires_at TIMESTAMPTZ NOT NULL,
        used_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS sent_items (
        url TEXT PRIMARY KEY,
        title TEXT,
        source TEXT,
        section TEXT,
        sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS delivery_logs (
        subscriber_id BIGINT NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
        campaign_key TEXT NOT NULL,
        resend_message_id TEXT,
        status TEXT NOT NULL CHECK (status IN ('sent', 'failed')),
        error TEXT,
        sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (subscriber_id, campaign_key)
    );

    CREATE TABLE IF NOT EXISTS rate_limits (
        key TEXT NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS newsletter_archives (
        campaign_key TEXT PRIMARY KEY,
        html_content TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS campaign_feedback (
        id SERIAL PRIMARY KEY,
        campaign_key TEXT NOT NULL,
        subscriber_email TEXT NOT NULL,
        vote TEXT NOT NULL CHECK (vote IN ('up', 'down')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (campaign_key, subscriber_email)
    );

    CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers (status);
    CREATE INDEX IF NOT EXISTS idx_tokens_lookup ON subscriber_tokens (purpose, token_hash, used_at, expires_at);
    CREATE INDEX IF NOT EXISTS idx_delivery_campaign ON delivery_logs (campaign_key, status);
    CREATE INDEX IF NOT EXISTS idx_rate_limits_key_timestamp ON rate_limits (key, timestamp);
    """)

def downgrade() -> None:
    op.execute("""
    DROP TABLE IF EXISTS campaign_feedback;
    DROP TABLE IF EXISTS newsletter_archives;
    DROP TABLE IF EXISTS rate_limits;
    DROP TABLE IF EXISTS delivery_logs;
    DROP TABLE IF EXISTS sent_items;
    DROP TABLE IF EXISTS subscriber_tokens;
    DROP TABLE IF EXISTS subscribers;
    """)
