import os
from unittest.mock import patch, MagicMock

os.environ["NEWSLETTER_TOKEN_SECRET"] = "test-secret"

import pytest
from src.persistence import _normalize_email, _hash_token, _utcnow, close_pool, _get_pool


def teardown_module():
    close_pool()


def test_normalize_email_strips_whitespace():
    assert _normalize_email("  Test@Example.com  ") == "test@example.com"


def test_normalize_email_lowercases():
    assert _normalize_email("USER@DOMAIN.COM") == "user@domain.com"


def test_normalize_email_empty():
    assert _normalize_email("") == ""


def test_utcnow_returns_utc_datetime():
    from datetime import timezone
    now = _utcnow()
    assert now.tzinfo is not None
    assert now.tzinfo.utcoffset(now) == timezone.utc.utcoffset(now)


def test_hash_token_consistent():
    assert _hash_token("token123") == _hash_token("token123")


def test_hash_token_different_for_different_inputs():
    assert _hash_token("abc") != _hash_token("xyz")


def test_hash_token_raises_without_secret():
    with patch("src.persistence.NEWSLETTER_TOKEN_SECRET", ""):
        with pytest.raises(EnvironmentError, match="NEWSLETTER_TOKEN_SECRET"):
            _hash_token("anything")


@patch("src.persistence.ConnectionPool")
def test_get_pool_returns_singleton(mock_pool):
    mock_pool.side_effect = lambda *a, **kw: MagicMock()
    p1 = _get_pool()
    p2 = _get_pool()
    assert p1 is p2
    close_pool()
    p3 = _get_pool()
    assert p3 is not p1
    close_pool()


def test_get_pool_fails_without_db_url():
    close_pool()
    with patch("src.persistence.DATABASE_URL", ""):
        with patch("src.persistence.ConnectionPool") as mock_pool_cls:
            mock_pool_cls.side_effect = ValueError("dsn must not be empty")
            with pytest.raises(ValueError, match="dsn must not be empty"):
                _get_pool()
    close_pool()
