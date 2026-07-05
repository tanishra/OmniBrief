from src.processor import similarity, normalize_url, get_tokens


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
