import httpx
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.fetchers.github_trending import fetch_github_trending


MOCK_GITHUB_RESPONSE = {
    "items": [
        {
            "html_url": "https://github.com/example/repo1",
            "full_name": "example/repo1",
            "name": "repo1",
            "description": "An AI-powered tool",
            "stargazers_count": 1500,
            "forks_count": 300,
            "owner": {"login": "example"},
        }
    ]
}


@pytest.mark.asyncio
async def test_fetch_github_trending_returns_repos():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: MOCK_GITHUB_RESPONSE

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_github_trending(queries=["machine learning"], max_items=5)

    assert len(results) >= 1
    r = results[0]
    assert r["url"] == "https://github.com/example/repo1"
    assert r["title"] == "example/repo1"
    assert r["stars"] == 1500


@pytest.mark.asyncio
async def test_fetch_github_trending_handles_non_200():
    mock_resp = AsyncMock()
    mock_resp.status_code = 403
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("forbidden", request=MagicMock(), response=mock_resp)

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_github_trending(queries=["ai"], max_items=5)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_fetch_github_trending_deduplicates():
    dup_resp = {
        "items": [
            {"html_url": "https://github.com/dup/repo", "name": "repo", "description": "desc", "stargazers_count": 100, "forks_count": 10, "owner": {"login": "dup"}},
            {"html_url": "https://github.com/dup/repo", "name": "repo", "description": "desc", "stargazers_count": 100, "forks_count": 10, "owner": {"login": "dup"}},
        ]
    }
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: dup_resp

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_github_trending(queries=["ai"], max_items=5)
    # Each query triggers multiple strategies, but URLs within same item should dedup
    seen = [r["url"] for r in results]
    assert len(seen) == len(set(seen))
