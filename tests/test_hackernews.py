import httpx
import pytest
from unittest.mock import AsyncMock, patch

from src.fetchers.hackernews import fetch_hackernews, AI_KEYWORDS


MOCK_ALGOLIA_RESPONSE = {
    "hits": [
        {
            "title": "New RLHF technique improves LLM alignment",
            "url": "https://example.com/rlhf",
            "objectID": "123",
            "points": 120,
            "num_comments": 45,
        },
        {
            "title": "Some random post about cooking",
            "url": "https://example.com/cooking",
            "objectID": "456",
            "points": 10,
            "num_comments": 2,
        },
    ]
}


@pytest.mark.asyncio
async def test_fetch_hackernews_returns_matching_items():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: MOCK_ALGOLIA_RESPONSE

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_hackernews(max_items=5)

    assert len(results) == 1
    assert results[0]["title"] == "New RLHF technique improves LLM alignment"
    assert results[0]["url"] == "https://example.com/rlhf"
    assert results[0]["points"] == 120
    assert results[0]["comments"] == 45


@pytest.mark.asyncio
async def test_fetch_hackernews_empty_when_no_match():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: {"hits": [{"title": "My cat video", "url": "https://x.com", "objectID": "789", "points": 200, "num_comments": 100}]}

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_hackernews(max_items=5)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_fetch_hackernews_handles_missing_fields():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: {"hits": [{"title": " AI agent ", "objectID": "111", "points": 80, "num_comments": 10}]}

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_hackernews(max_items=5)
    assert len(results) == 1
    # When url is missing, fetcher builds one from objectID
    assert results[0]["url"] == "https://news.ycombinator.com/item?id=111"


@pytest.mark.asyncio
async def test_fetch_hackernews_returns_at_most_max_items():
    hits = [
        {"title": f"AI breakthrough {i}", "url": f"https://x.com/{i}", "objectID": str(i), "points": 100, "num_comments": 10}
        for i in range(10)
    ]
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: {"hits": hits}

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_hackernews(max_items=3)
    assert len(results) == 3


def test_ai_keywords_contains_relevant_terms():
    assert "llm" in AI_KEYWORDS
    assert "transformer" in AI_KEYWORDS
    assert "agent" in AI_KEYWORDS
