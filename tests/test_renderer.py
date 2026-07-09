import pytest
from src.renderer import render_digest


@pytest.fixture
def sample_data():
    return {
        "hn": [
            {"title": "HN Post", "url": "https://news.ycombinator.com/item?id=1", "points": 100}
        ],
        "news": [],
        "arxiv": [
            {"title": "ArXiv Paper", "url": "https://arxiv.org/abs/2401.00001", "authors": "Author et al."}
        ],
        "github": [
            {"name": "GitHub Repo", "title": "GitHub Repo", "url": "https://github.com/user/repo", "stars": 500}
        ],
        "ph": [],
        "reddit": [
            {"title": "Reddit Post", "url": "https://reddit.com/r/ai/post", "score": 200}
        ],
    }


def test_render_digest_returns_string(sample_data):
    html = render_digest(sample_data)
    assert isinstance(html, str)
    assert len(html) > 0


def test_render_digest_includes_section_titles(sample_data):
    html = render_digest(sample_data)
    assert "HN Post" in html
    assert "ArXiv Paper" in html
    assert "GitHub Repo" in html
    assert "Reddit Post" in html


def test_render_digest_includes_synthesis():
    html = render_digest({"hn": [], "news": [], "arxiv": [], "github": [], "ph": [], "reddit": []}, synthesis="<p>Test synthesis</p>")
    assert "Test synthesis" in html


def test_render_digest_includes_unsubscribe_url():
    html = render_digest({"hn": [], "news": [], "arxiv": [], "github": [], "ph": [], "reddit": []}, unsubscribe_url="https://example.com/unsub")
    assert "example.com/unsub" in html


def test_render_digest_uses_stats_placeholder(sample_data):
    html = render_digest(sample_data)
    assert "papers" in html.lower() or "1 paper" in html.lower()


def test_render_digest_empty_data():
    html = render_digest({"hn": [], "news": [], "arxiv": [], "github": [], "ph": [], "reddit": []})
    assert isinstance(html, str)
    assert len(html) > 0
