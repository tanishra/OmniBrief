from src.processor import deduplicate_and_correlate, get_tokens, similarity

def test_get_tokens():
    assert get_tokens("Hello World 2024!") == {"hello", "world", "2024"}
    assert get_tokens("  Extra   Spaces  ") == {"extra", "spaces"}
    assert get_tokens("Punctuation... and, symbols?") == {"punctuation", "and", "symbols"}

def test_similarity():
    assert similarity("A new model by OpenAI", "a new model by openai") == 1.0
    assert similarity("Apples are good", "FastAPI is cool") == 0.0

def test_deduplicate_and_correlate():
    data = {
        "arxiv": [
            {"title": "Attention Is All You Need", "abstract": "We propose a new simple network architecture, the Transformer..."},
            {"title": "Some other paper", "abstract": "abc"}
        ],
        "github": [
            {"name": "transformer", "title": "Attention Is All You Need"}
        ],
        "hn": [
            {"title": "Attention Is All You Need (2017)"}
        ],
        "reddit": []
    }

    clean_data = deduplicate_and_correlate(data)

    assert len(clean_data["arxiv"]) == 2
    assert "implemented_by" in clean_data["arxiv"][0]
    assert len(clean_data["github"]) == 0
    assert len(clean_data["hn"]) == 0
