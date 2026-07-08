import socket
from unittest.mock import patch

from src.scraper import _resolve_and_check_safe


def test_resolve_accepts_https():
    with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("8.8.8.8", 0))]):
        result = _resolve_and_check_safe("https://example.com")
    assert result == "8.8.8.8"


def test_resolve_blocks_private_literal_ip():
    assert _resolve_and_check_safe("http://127.0.0.1") is None
    assert _resolve_and_check_safe("http://10.0.0.1") is None
    assert _resolve_and_check_safe("http://192.168.1.1") is None
    assert _resolve_and_check_safe("http://172.16.0.1") is None


def test_resolve_allows_public_literal_ip():
    assert _resolve_and_check_safe("http://8.8.8.8") == "8.8.8.8"
    assert _resolve_and_check_safe("http://1.1.1.1") == "1.1.1.1"


def test_resolve_blocks_resolved_private_ip():
    with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("10.0.0.5", 0))]):
        result = _resolve_and_check_safe("http://internal.example.com")
    assert result is None


def test_resolve_allows_resolved_public_ip():
    with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("8.8.8.8", 0))]):
        result = _resolve_and_check_safe("http://public.example.com")
    assert result == "8.8.8.8"


def test_resolve_dns_failure_allows_through():
    with patch("socket.getaddrinfo", side_effect=socket.gaierror):
        result = _resolve_and_check_safe("http://transient-failure.example.com")
    assert result == "transient-failure.example.com"


def test_resolve_rejects_non_http():
    assert _resolve_and_check_safe("ftp://files.example.com") is None
    assert _resolve_and_check_safe("file:///etc/passwd") is None


def test_resolve_rejects_empty_hostname():
    assert _resolve_and_check_safe("http://") is None


def test_resolve_blocks_link_local_ip():
    assert _resolve_and_check_safe("http://169.254.1.1") is None


def test_resolve_blocks_multicast_ip():
    assert _resolve_and_check_safe("http://224.0.0.1") is None


def test_resolve_blocks_loopback_ip():
    assert _resolve_and_check_safe("http://0.0.0.0") is None
