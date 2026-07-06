import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.fetchers.producthunt import fetch_producthunt

PH_RSS = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>AI Product (42 votes)</title>
      <link>https://www.producthunt.com/posts/ai-product</link>
      <description>An amazing AI product description with <b>HTML</b>.</description>
      <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Another Product (7 votes)</title>
      <link>https://www.producthunt.com/posts/another-product</link>
      <description>Another description.</description>
      <pubDate>Tue, 02 Jan 2024 00:00:00 GMT</pubDate>
    </item>
    <item>
      <title>No Votes Product</title>
      <link>https://www.producthunt.com/posts/no-votes</link>
      <description>No votes in title.</description>
      <pubDate>Wed, 03 Jan 2024 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


def _mock_httpx(text: str):
    mock_resp = MagicMock()
    mock_resp.text = text
    mock_resp.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_resp
    return mock_client


def test_fetch_producthunt_parses_items():
    mock_client = _mock_httpx(PH_RSS)
    with patch("httpx.AsyncClient", return_value=mock_client):
        items = asyncio.run(fetch_producthunt(max_items=5))
    assert len(items) == 3
    assert items[0]["title"] == "AI Product"
    assert items[0]["url"] == "https://www.producthunt.com/posts/ai-product"
    assert items[0]["votes"] == 42
    assert items[0]["source"] == "ProductHunt"


def test_fetch_producthunt_extracts_votes():
    mock_client = _mock_httpx(PH_RSS)
    with patch("httpx.AsyncClient", return_value=mock_client):
        items = asyncio.run(fetch_producthunt(max_items=5))
    assert items[0]["votes"] == 42
    assert items[1]["votes"] == 7
    assert items[2]["votes"] == 0
    assert items[2]["title"] == "No Votes Product"


def test_fetch_producthunt_respects_max_items():
    mock_client = _mock_httpx(PH_RSS)
    with patch("httpx.AsyncClient", return_value=mock_client):
        items = asyncio.run(fetch_producthunt(max_items=1))
    assert len(items) == 1


def test_fetch_producthunt_empty_on_error():
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("HTTP error")
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_resp
    with patch("httpx.AsyncClient", return_value=mock_client):
        items = asyncio.run(fetch_producthunt(max_items=5))
    assert items == []
