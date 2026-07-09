import httpx
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.fetchers.reddit import fetch_reddit


MOCK_REDDIT_JSON = {
    "data": {
        "children": [
            {
                "data": {
                    "title": "Claude 4 is amazing for coding",
                    "url": "https://reddit.com/r/ai/post1",
                    "subreddit": "artificial",
                    "score": 500,
                    "num_comments": 120,
                    "permalink": "/r/artificial/comments/post1/",
                }
            },
            {
                "data": {
                    "title": "What is the best pizza topping?",
                    "url": "https://reddit.com/r/food/post2",
                    "subreddit": "food",
                    "score": 50,
                    "num_comments": 200,
                    "permalink": "/r/food/comments/post2/",
                }
            },
        ]
    }
}


@pytest.mark.asyncio
async def test_fetch_reddit_returns_ai_matching_posts():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: MOCK_REDDIT_JSON

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_reddit(subreddits=["artificial"], max_items=5)

    assert len(results) == 1
    assert results[0]["title"] == "Claude 4 is amazing for coding"
    assert results[0]["score"] == 500


@pytest.mark.asyncio
async def test_fetch_reddit_empty_when_no_match():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: {"data": {"children": [{"data": {"title": "My favorite recipe", "url": "https://x.com", "subreddit": "food", "score": 10, "num_comments": 5, "permalink": "/r/food/3/"}}]}}

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_reddit(subreddits=["food"], max_items=5)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_fetch_reddit_tries_multiple_endpoints():
    mock_posts = [
        {"data": {"title": "Claude 4 is amazing for coding", "url": "https://reddit.com/r/ai/post1", "subreddit": "artificial", "score": 500, "num_comments": 120, "permalink": "/r/artificial/comments/post1/"}}
    ]

    with patch("src.fetchers.reddit._fetch_subreddit_posts", new=AsyncMock(return_value=mock_posts)):
        results = await fetch_reddit(subreddits=["artificial"], max_items=5)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_fetch_reddit_returns_empty_on_all_fail():
    with patch("src.fetchers.reddit._fetch_subreddit_posts", new=AsyncMock(return_value=[])):
        results = await fetch_reddit(subreddits=["artificial"], max_items=5)
    assert len(results) == 0
