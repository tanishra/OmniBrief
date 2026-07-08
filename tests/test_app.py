import src.persistence  # noqa: F401 — ensure module is loaded before patching
from unittest.mock import patch

from fastapi.testclient import TestClient

# Patch app-level references BEFORE importing app
patch_init_db = patch("src.persistence.init_db")
patch_init_db.start()

patch_rate = patch("app.enforce_rate_limit", return_value=True)
patch_rate.start()

mock_upsert = patch("app.upsert_pending_subscriber").start()
mock_upsert.return_value = {"status": "pending", "email": "test@example.com", "id": "123"}

patch_confirm_link = patch("app.create_confirm_link", return_value="https://example.com/confirm?token=abc")
patch_confirm_link.start()

mock_confirm = patch("app.confirm_subscriber").start()
mock_confirm.return_value = {"email": "test@example.com"}

mock_unsub = patch("app.unsubscribe_subscriber").start()
mock_unsub.return_value = {"email": "test@example.com"}

patch_feedback = patch("app.record_feedback")
patch_feedback.start()

patch_mailer = patch("app.send_confirmation_email")
patch_mailer.start()

from app import app

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_subscribe_new():
    mock_upsert.return_value = {"status": "pending", "email": "test@example.com", "id": "123"}
    resp = client.post("/subscribe", json={"email": "test@example.com"})
    assert resp.status_code == 200
    assert "confirmation email" in resp.json()["message"].lower()


def test_subscribe_already_active():
    mock_upsert.return_value = {"status": "active", "email": "test@example.com"}
    resp = client.post("/subscribe", json={"email": "test@example.com"})
    assert resp.status_code == 200
    assert "already" in resp.json()["message"].lower()


def test_subscribe_missing_email():
    resp = client.post("/subscribe", json={})
    assert resp.status_code == 422


def test_subscribe_invalid_email():
    resp = client.post("/subscribe", json={"email": "not-an-email"})
    assert resp.status_code == 422


def test_confirm_page_renders():
    resp = client.get("/confirm?token=abc123")
    assert resp.status_code == 200
    assert "Confirm" in resp.text


def test_confirm_post_invalid_token():
    mock_confirm.return_value = None
    resp = client.post("/confirm", data={"token": "invalid"})
    assert resp.status_code == 200
    assert "invalid" in resp.text.lower()


def test_confirm_post_valid_token():
    mock_confirm.return_value = {"email": "test@example.com"}
    resp = client.post("/confirm", data={"token": "valid"})
    assert resp.status_code == 200
    assert "confirmed" in resp.text.lower()


def test_unsubscribe_page_renders():
    resp = client.get("/unsubscribe?token=abc123")
    assert resp.status_code == 200
    assert "Unsubscribe" in resp.text


def test_unsubscribe_post_invalid_token():
    mock_unsub.return_value = None
    resp = client.post("/unsubscribe", data={"token": "invalid"})
    assert resp.status_code == 200
    assert "invalid" in resp.text.lower()


def test_unsubscribe_post_valid_token():
    mock_unsub.return_value = {"email": "test@example.com"}
    resp = client.post("/unsubscribe", data={"token": "valid"})
    assert resp.status_code == 200
    assert "unsubscribed" in resp.text.lower()


def test_feedback_invalid_signature():
    resp = client.get("/feedback?campaign=2024-01-01&email=test@example.com&vote=up&sig=invalid")
    assert resp.status_code == 200
    assert "invalid" in resp.text.lower()


def test_feedback_invalid_vote():
    from app import _generate_feedback_hmac
    sig = _generate_feedback_hmac("2024-01-01", "test@example.com", "bad")
    resp = client.get(f"/feedback?campaign=2024-01-01&email=test@example.com&vote=bad&sig={sig}")
    assert resp.status_code == 200
    assert "invalid" in resp.text.lower()


def test_feedback_valid_vote_up():
    from app import _generate_feedback_hmac
    sig = _generate_feedback_hmac("2024-01-01", "test@example.com", "up")
    resp = client.get(f"/feedback?campaign=2024-01-01&email=test@example.com&vote=up&sig={sig}")
    assert resp.status_code == 200
    assert "glad" in resp.text.lower()
