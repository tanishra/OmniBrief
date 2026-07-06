import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.fetchers.rss_feeds import fetch_rss_feeds

RSS_XML = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Test Article</title>
      <link>https://example.com/article</link>
      <description>Description with <b>HTML</b> tags.</description>
      <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Second Article</title>
      <link>https://example.com/second</link>
      <description>Second description.</description>
      <pubDate>Tue, 02 Jan 2024 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

ATOM_XML = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Atom Article</title>
    <link href="https://example.com/atom"/>
    <content>Atom content with <b>HTML</b>.</content>
    <published>2024-01-03T00:00:00Z</published>
  </entry>
</feed>"""


def _mock_httpx(text: str):
    mock_resp = MagicMock()
    mock_resp.text = text
    mock_resp.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_resp
    return mock_client


def test_fetch_rss_feeds_parses_rss():
    mock_client = _mock_httpx(RSS_XML)
    with patch("httpx.AsyncClient", return_value=mock_client):
        feeds = [{"name": "Test Feed", "url": "https://example.com/rss", "category": "news"}]
        items = asyncio.run(fetch_rss_feeds(feeds, max_per_feed=5))
    assert len(items) == 2
    assert items[0]["title"] == "Test Article"
    assert items[0]["url"] == "https://example.com/article"
    assert items[0]["summary"] == "Description with HTML tags."
    assert items[0]["source"] == "Test Feed"
    assert items[0]["category"] == "news"
    assert items[1]["title"] == "Second Article"


def test_fetch_rss_feeds_parses_atom():
    mock_client = _mock_httpx(ATOM_XML)
    with patch("httpx.AsyncClient", return_value=mock_client):
        feeds = [{"name": "Atom Feed", "url": "https://example.com/atom", "category": "research"}]
        items = asyncio.run(fetch_rss_feeds(feeds, max_per_feed=5))
    assert len(items) == 1
    assert items[0]["title"] == "Atom Article"
    assert items[0]["url"] == "https://example.com/atom"
    assert items[0]["source"] == "Atom Feed"
    assert items[0]["category"] == "research"


def test_fetch_rss_feeds_empty_on_http_error():
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("HTTP error")
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_resp
    with patch("httpx.AsyncClient", return_value=mock_client):
        feeds = [{"name": "Bad Feed", "url": "https://example.com/bad", "category": "news"}]
        items = asyncio.run(fetch_rss_feeds(feeds, max_per_feed=5))
    assert items == []


def test_fetch_rss_feeds_respects_max_per_feed():
    mock_client = _mock_httpx(RSS_XML)
    with patch("httpx.AsyncClient", return_value=mock_client):
        feeds = [{"name": "Test Feed", "url": "https://example.com/rss", "category": "news"}]
        items = asyncio.run(fetch_rss_feeds(feeds, max_per_feed=1))
    assert len(items) == 1
