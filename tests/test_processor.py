from src.processor import similarity, normalize_url, get_tokens, deduplicate_and_correlate


def test_get_tokens():
    assert get_tokens("Hello World!") == {"hello", "world"}
    assert get_tokens("") == set()


def test_similarity_identical():
    assert similarity("Hello World", "Hello World") == 1.0


def test_similarity_disjoint():
    assert similarity("abc def", "ghi jkl") == 0.0


def test_similarity_partial():
    sim = similarity("AI agent framework", "AI agent autonomous")
    assert 0.3 < sim < 0.8


def test_similarity_empty():
    assert similarity("", "anything") == 0.0
    assert similarity("anything", "") == 0.0
    assert similarity("", "") == 0.0


def test_normalize_url_strips_query():
    assert normalize_url("http://example.com/page?ref=hn") == "http://example.com/page"


def test_normalize_url_strips_fragment():
    assert normalize_url("http://example.com/page#section") == "http://example.com/page"


def test_normalize_url_preserves_path():
    assert normalize_url("http://example.com/a/b/c") == "http://example.com/a/b/c"


def test_normalize_url_handles_no_path():
    assert normalize_url("http://example.com") == "http://example.com"


def test_dedup_same_title_different_sources():
    data = {
        "hn": [{"title": "AI Breakthrough", "url": "https://news.ycombinator.com/item?id=1"}],
        "reddit": [{"title": "AI Breakthrough", "url": "https://reddit.com/r/ml/comments/1"}],
    }
    result = deduplicate_and_correlate(data)
    assert len(result["hn"]) == 1
    assert len(result["reddit"]) == 0


def test_dedup_same_url_different_titles():
    data = {
        "hn": [{"title": "Article A", "url": "https://example.com/article"}],
        "news": [{"title": "Article A - Updated", "url": "https://example.com/article?ref=news"}],
    }
    result = deduplicate_and_correlate(data)
    assert len(result["hn"]) == 1
    assert len(result["news"]) == 0


def test_dedup_passes_different_items():
    data = {
        "hn": [{"title": "AI Research Paper", "url": "https://example.com/ai"}],
        "reddit": [{"title": "Python 3.13 Released", "url": "https://example.com/python"}],
    }
    result = deduplicate_and_correlate(data)
    assert len(result["hn"]) == 1
    assert len(result["reddit"]) == 1


def test_dedup_empty_input():
    assert deduplicate_and_correlate({}) == {}


def test_correlation_arxiv_github_match():
    data = {
        "arxiv": [{"title": "Fast Transformer", "url": "https://arxiv.org/abs/2401.001", "abstract": "We introduce transformer-lm a new model"}],
        "github": [{"name": "user/transformer-lm", "url": "https://github.com/user/transformer-lm"}],
    }
    result = deduplicate_and_correlate(data)
    assert len(result["arxiv"]) == 1
    assert "implemented_by" in result["arxiv"][0]
    assert result["arxiv"][0]["implemented_by"]["name"] == "user/transformer-lm"


def test_correlation_arxiv_no_match():
    data = {
        "arxiv": [{"title": "Fast Transformer", "url": "https://arxiv.org/abs/2401.001", "abstract": "A new transformer architecture"}],
        "github": [{"name": "user/unrelated-tool", "url": "https://github.com/user/unrelated-tool"}],
    }
    result = deduplicate_and_correlate(data)
    assert len(result["arxiv"]) == 1
    assert "implemented_by" not in result["arxiv"][0]
