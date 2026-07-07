from src.summarizer import _sanitize_input, _get_system_prompt


def test_sanitize_input_strips_html():
    assert _sanitize_input("<b>hello</b>") == "hello"


def test_sanitize_input_removes_angle_brackets():
    assert _sanitize_input("foo <bar> baz") == "foo  baz"


def test_sanitize_input_handles_nested_tags():
    assert _sanitize_input("<div><span>nested</span></div>") == "nested"


def test_sanitize_input_empty_string():
    assert _sanitize_input("") == ""


def test_sanitize_input_no_tags():
    assert _sanitize_input("hello world") == "hello world"


def test_get_system_prompt_contains_delimiter():
    prompt = _get_system_prompt("abc123")
    assert "abc123" in prompt


def test_get_system_prompt_contains_mission():
    prompt = _get_system_prompt("x")
    assert "CORE MISSION" in prompt


def test_get_system_prompt_contains_security():
    prompt = _get_system_prompt("x")
    assert "SECURITY INSTRUCTION" in prompt


def test_get_system_prompt_different_delimiters():
    prompt_a = _get_system_prompt("token_a")
    prompt_b = _get_system_prompt("token_b")
    assert "token_a" in prompt_a
    assert "token_b" in prompt_b
    assert "token_a" not in prompt_b
