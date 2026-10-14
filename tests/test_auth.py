import pytest
from fastapi.testclient import TestClient

def test_successful_registration(client: TestClient):
    payload = {
        "username": "fresh_user",
        "email": "fresh@example.com",
        "password": "SecurePassword1"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "fresh_user"
    assert data["email"] == "fresh@example.com"
    assert "password" not in data
    assert "password_hash" not in data
    assert "pyassist_session" in response.cookies

def test_duplicate_username_and_email(client: TestClient, registered_user):
    # Same username, different email
    dup_user = {
        "username": registered_user["credentials"]["username"],
        "email": "different@example.com",
        "password": "Password123"
    }
    res1 = client.post("/api/auth/register", json=dup_user)
    assert res1.status_code == 409
    assert "already exists" in res1.json()["detail"].lower()

    # Different username, same email
    dup_email = {
        "username": "totally_unique",
        "email": registered_user["credentials"]["email"],
        "password": "Password123"
    }
    res2 = client.post("/api/auth/register", json=dup_email)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()

    # Account identifiers are case-insensitive for duplicate detection.
    case_variant = {
        "username": registered_user["credentials"]["username"].upper(),
        "email": "different2@example.com",
        "password": "Password123"
    }
    res3 = client.post("/api/auth/register", json=case_variant)
    assert res3.status_code == 409


def test_register_login_and_open_dashboard(client: TestClient):
    credentials = {
        "username": "submission_user",
        "email": "submission@example.com",
        "password": "SecurePassword123"
    }
    registration = client.post("/api/auth/register", json=credentials)
    assert registration.status_code == 201

    login = client.post("/api/auth/login", json={
        "username_or_email": credentials["email"],
        "password": credentials["password"]
    })
    assert login.status_code == 200
    cookies = login.cookies

    profile = client.get("/api/auth/me", cookies=cookies)
    assert profile.status_code == 200
    assert profile.json()["username"] == credentials["username"]

    dashboard = client.get("/", cookies=cookies)
    assert dashboard.status_code == 200
    assert "PyAssist" in dashboard.text

def test_invalid_registration_data(client: TestClient):
    # Short password
    short_pw = {
        "username": "valid_user",
        "email": "valid@example.com",
        "password": "pass1"
    }
    res = client.post("/api/auth/register", json=short_pw)
    assert res.status_code == 422

    # Password without digits
    no_digits = {
        "username": "valid_user2",
        "email": "valid2@example.com",
        "password": "passwordonly"
    }
    res = client.post("/api/auth/register", json=no_digits)
    assert res.status_code == 422

    # Malformed email
    bad_email = {
        "username": "valid_user3",
        "email": "not-an-email",
        "password": "Password123"
    }
    res = client.post("/api/auth/register", json=bad_email)
    assert res.status_code == 422

def test_successful_login_and_cookie(client: TestClient, registered_user):
    payload = {
        "username_or_email": registered_user["credentials"]["username"],
        "password": registered_user["credentials"]["password"]
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    assert "pyassist_session" in response.cookies
    assert response.json()["username"] == registered_user["user"]["username"]

def test_login_with_email(client: TestClient, registered_user):
    payload = {
        "username_or_email": registered_user["credentials"]["email"],
        "password": registered_user["credentials"]["password"]
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == registered_user["user"]["id"]

def test_incorrect_credentials(client: TestClient, registered_user):
    payload = {
        "username_or_email": registered_user["credentials"]["username"],
        "password": "WrongPassword999"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid username/email or password" in response.json()["detail"]

def test_logout_and_session_revocation(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    # User profile works
    res_me = client.get("/api/auth/me", cookies=cookies)
    assert res_me.status_code == 200

    # Logout
    res_logout = client.post(
        "/api/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf_token}
    )
    assert res_logout.status_code == 200

    # After logout, accessing protected route with revoked cookie fails
    res_after = client.get("/api/auth/me", cookies=cookies)
    assert res_after.status_code == 401

def test_unauthenticated_access_to_protected_routes(client: TestClient):
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 401

    res_history = client.get("/api/history")
    assert res_history.status_code == 401

    res_chat = client.post("/api/chat/ask", json={"question": "What is Python?"})
    assert res_chat.status_code == 401
