import pytest
from fastapi.testclient import TestClient
from pyassist.app.config import settings

def test_session_cookie_security_attributes(client: TestClient):
    payload = {
        "username": "cookie_tester",
        "email": "cookie@example.com",
        "password": "Password123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    session_cookie = response.cookies.get(settings.SESSION_COOKIE_NAME)
    assert session_cookie is not None

    # Check Set-Cookie header contains HttpOnly and SameSite
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie_header or "httponly" in set_cookie_header.lower()
    assert f"samesite={settings.COOKIE_SAMESITE}" in set_cookie_header.lower()

def test_csrf_protection_on_state_changing_requests(client: TestClient, registered_user):
    cookies = registered_user["cookies"]

    # Attempt to post a chat message without CSRF token header
    res_no_csrf = client.post(
        "/api/chat/ask",
        cookies=cookies,
        json={"question": "What is Python?"}
    )
    # Must be rejected with 403 Forbidden
    assert res_no_csrf.status_code == 403
    assert "CSRF" in res_no_csrf.json()["detail"]

    # Attempt with invalid CSRF token
    res_bad_csrf = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": "tampered_fake_csrf_token"},
        json={"question": "What is Python?"}
    )
    assert res_bad_csrf.status_code == 403

def test_html_like_user_input_stored_safely(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf = cookies.get("pyassist_csrf", "")

    malicious_input = "<script>alert('xss')</script> What is a function?"
    res = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf},
        json={"question": malicious_input}
    )
    assert res.status_code == 200
    user_msg = res.json()["user_message"]
    # Saved text is preserved as raw text without execution
    assert user_msg["content"] == malicious_input

def test_health_check_does_not_leak_internals(client: TestClient):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["app"] == "PyAssist"
    assert "secret" not in str(data).lower()
    assert "password" not in str(data).lower()
    assert "/app/" not in str(data)  # no internal server path leaked
