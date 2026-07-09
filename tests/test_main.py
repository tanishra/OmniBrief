import os
os.environ["NEWSLETTER_TOKEN_SECRET"] = "test-secret-for-hmac"
os.environ["DATABASE_URL"] = "postgres://user:pass@localhost:5432/test"
os.environ["APP_BASE_URL"] = "http://localhost:8000"

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from main import fetch_raw_data, _build_feedback_url, _generate_feedback_hmac


@pytest.mark.asyncio
async def test_fetch_raw_data_combines_all_sources():
    mock_hn = AsyncMock(return_value=[{"title": "HN item", "url": "https://hn/1"}])
    mock_rss = AsyncMock(return_value=[{"title": "RSS item", "url": "https://rss/1"}])
    mock_arxiv = AsyncMock(return_value=[{"title": "ArXiv item", "url": "https://arxiv/1"}])
    mock_github = AsyncMock(return_value=[{"title": "GitHub item", "url": "https://github/1"}])
    mock_ph = AsyncMock(return_value=[{"title": "PH item", "url": "https://ph/1"}])
    mock_reddit = AsyncMock(return_value=[{"title": "Reddit item", "url": "https://reddit/1"}])

    patches = [
        patch("main.fetch_hackernews", mock_hn),
        patch("main.fetch_rss_feeds", mock_rss),
        patch("main.fetch_arxiv", mock_arxiv),
        patch("main.fetch_github_trending", mock_github),
        patch("main.fetch_producthunt", mock_ph),
        patch("main.fetch_reddit", mock_reddit),
    ]

    with patch("main.HN_MAX_ITEMS", 10), patch("main.RSS_MAX_PER_FEED", 3), \
         patch("main.ARXIV_MAX_ITEMS", 10), patch("main.GITHUB_TRENDING_MAX", 20), \
         patch("main.PRODUCTHUNT_MAX", 10), patch("main.REDDIT_MAX_ITEMS", 10):
        with patch("main.RSS_FEEDS", [{"name": "test", "url": "https://test/rss", "category": "news"}]):
            with patch("main.GITHUB_QUERIES", ["ai"]), patch("main.AI_ORGANIZATIONS", []):
                with patch("main.GITHUB_TOKEN", ""):
                    for p in patches:
                        p.start()
                    try:
                        data, stats = await fetch_raw_data()
                    finally:
                        for p in reversed(patches):
                            p.stop()

    assert "hn" in data
    assert "news" in data
    assert "arxiv" in data
    assert "github" in data
    assert "ph" in data
    assert "reddit" in data
    assert len(data["hn"]) == 1
    assert len(data["news"]) == 1


@pytest.mark.asyncio
async def test_fetch_raw_data_handles_failures_gracefully():
    """When a fetcher raises, that section should be empty, not crash."""
    mock_ok = AsyncMock(return_value=[{"title": "ok", "url": "https://ok"}])
    mock_fail = AsyncMock(side_effect=Exception("Network error"))

    patches = [
        patch("main.fetch_hackernews", mock_fail),
        patch("main.fetch_rss_feeds", mock_fail),
        patch("main.fetch_arxiv", mock_fail),
        patch("main.fetch_github_trending", mock_fail),
        patch("main.fetch_producthunt", mock_ok),
        patch("main.fetch_reddit", mock_fail),
    ]

    with patch("main.HN_MAX_ITEMS", 10), patch("main.RSS_MAX_PER_FEED", 3), \
         patch("main.ARXIV_MAX_ITEMS", 10), patch("main.GITHUB_TRENDING_MAX", 20), \
         patch("main.PRODUCTHUNT_MAX", 10), patch("main.REDDIT_MAX_ITEMS", 10):
        with patch("main.RSS_FEEDS", []), patch("main.GITHUB_QUERIES", []), \
             patch("main.AI_ORGANIZATIONS", []), patch("main.GITHUB_TOKEN", ""):
            for p in patches:
                p.start()
            try:
                data, stats = await fetch_raw_data()
            finally:
                for p in reversed(patches):
                    p.stop()

    assert len(data["hn"]) == 0
    assert len(data["news"]) == 0
    assert len(data["ph"]) == 1
    for k, v in data.items():
        assert isinstance(v, list)


def test_generate_feedback_hmac_consistency():
    sig1 = _generate_feedback_hmac("2024-01-01", "user@test.com", "up")
    sig2 = _generate_feedback_hmac("2024-01-01", "user@test.com", "up")
    assert sig1 == sig2


def test_generate_feedback_hmac_differs_for_vote():
    up = _generate_feedback_hmac("2024-01-01", "user@test.com", "up")
    down = _generate_feedback_hmac("2024-01-01", "user@test.com", "down")
    assert up != down


def test_build_feedback_url_includes_params():
    url = _build_feedback_url("2024-01-01", "user@test.com", "up")
    assert "campaign=2024-01-01" in url
    assert "email=user%40test.com" in url
    assert "vote=up" in url
    assert "sig=" in url
