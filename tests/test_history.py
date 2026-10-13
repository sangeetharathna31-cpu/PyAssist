import pytest
from fastapi.testclient import TestClient

def test_conversation_persistence_and_retrieval(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    # Ask first question -> creates conversation
    res1 = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf_token},
        json={"question": "What is Python?"}
    )
    assert res1.status_code == 200
    conv_id = res1.json()["conversation_id"]

    # Ask second question in the same conversation
    res2 = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf_token},
        json={
            "question": "Explain list comprehensions.",
            "conversation_id": conv_id
        }
    )
    assert res2.status_code == 200
    assert res2.json()["conversation_id"] == conv_id

    # List conversations
    res_list = client.get("/api/history", cookies=cookies)
    assert res_list.status_code == 200
    history_list = res_list.json()
    assert any(c["id"] == conv_id for c in history_list)

    # Get conversation details
    res_detail = client.get(f"/api/history/{conv_id}", cookies=cookies)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == conv_id
    assert len(detail["messages"]) == 4  # 2 user msgs + 2 bot msgs

def test_cross_user_isolation_read(client: TestClient, registered_user, second_user):
    # User 1 creates conversation
    c1 = registered_user["cookies"]
    csrf1 = c1.get("pyassist_csrf", "")
    res = client.post(
        "/api/chat/ask",
        cookies=c1,
        headers={"X-CSRF-Token": csrf1},
        json={"question": "Explain classes and objects."}
    )
    assert res.status_code == 200
    user1_conv_id = res.json()["conversation_id"]

    # User 2 attempts to read User 1's conversation
    c2 = second_user["cookies"]
    res_unauth = client.get(f"/api/history/{user1_conv_id}", cookies=c2)
    assert res_unauth.status_code in (404, 403)
    assert "not found" in res_unauth.json()["detail"].lower() or "forbidden" in res_unauth.json()["detail"].lower()

def test_cross_user_isolation_delete(client: TestClient, registered_user, second_user):
    # User 1 creates conversation
    c1 = registered_user["cookies"]
    csrf1 = c1.get("pyassist_csrf", "")
    res = client.post(
        "/api/chat/ask",
        cookies=c1,
        headers={"X-CSRF-Token": csrf1},
        json={"question": "What is exception handling?"}
    )
    assert res.status_code == 200
    user1_conv_id = res.json()["conversation_id"]

    # User 2 attempts to delete User 1's conversation
    c2 = second_user["cookies"]
    csrf2 = c2.get("pyassist_csrf", "")
    res_del_attack = client.delete(
        f"/api/history/{user1_conv_id}",
        cookies=c2,
        headers={"X-CSRF-Token": csrf2}
    )
    assert res_del_attack.status_code in (404, 403)

    # Verify conversation still exists for User 1
    res_check = client.get(f"/api/history/{user1_conv_id}", cookies=c1)
    assert res_check.status_code == 200

def test_authorized_conversation_deletion(client: TestClient, registered_user):
    c = registered_user["cookies"]
    csrf = c.get("pyassist_csrf", "")

    # Create conversation
    res = client.post(
        "/api/chat/ask",
        cookies=c,
        headers={"X-CSRF-Token": csrf},
        json={"question": "How do I read a text file in Python?"}
    )
    conv_id = res.json()["conversation_id"]

    # User deletes own conversation
    res_del = client.delete(
        f"/api/history/{conv_id}",
        cookies=c,
        headers={"X-CSRF-Token": csrf}
    )
    assert res_del.status_code == 200

    # Verify it is gone
    res_get = client.get(f"/api/history/{conv_id}", cookies=c)
    assert res_get.status_code == 404
