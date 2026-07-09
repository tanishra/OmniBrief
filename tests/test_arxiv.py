import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.fetchers.arxiv import fetch_arxiv


SAMPLE_ARXIV_XML = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345</id>
    <title>Attention Is All You Need</title>
    <published>2024-01-15T00:00:00Z</published>
    <summary>We propose a new network architecture, the Transformer...</summary>
    <author><name>Vaswani et al.</name></author>
    <link href="http://arxiv.org/abs/2401.12345" rel="alternate" type="text/html"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.67890</id>
    <title>BERT: Pre-training of Deep Bidirectional Transformers</title>
    <published>2024-01-10T00:00:00Z</published>
    <summary>We introduce a new language representation model called BERT...</summary>
    <author><name>Devlin et al.</name></author>
    <link href="http://arxiv.org/abs/2401.67890" rel="alternate" type="text/html"/>
  </entry>
</feed>"""


@pytest.mark.asyncio
async def test_fetch_arxiv_returns_entries():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.text = SAMPLE_ARXIV_XML

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_arxiv(categories=["cs.AI"], max_items=5)

    assert len(results) == 2
    assert results[0]["title"] == "Attention Is All You Need"
    assert results[0]["url"] == "http://arxiv.org/abs/2401.12345"
    assert "Vaswani" in results[0]["authors"][0]
    assert "BERT" in results[1]["title"]


@pytest.mark.asyncio
async def test_fetch_arxiv_empty_on_no_results():
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.text = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>"""

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_arxiv(categories=["cs.CL"], max_items=5)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_fetch_arxiv_returns_empty_on_all_429s():
    """When all 3 retry attempts hit 429, fetch returns empty list."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 429

    with patch("src.fetchers.arxiv.httpx.AsyncClient.get", return_value=mock_resp):
        results = await fetch_arxiv(categories=["cs.AI"], max_items=5)
    assert len(results) == 0
