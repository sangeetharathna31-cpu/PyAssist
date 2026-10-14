import pytest
from fastapi.testclient import TestClient

def test_chat_known_python_questions(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    sample_questions = [
        ("What is Python?", "python_intro"),
        ("Explain lists and tuples.", "lists_vs_tuples"),
        ("What is the difference between a list and a dictionary?", "lists_vs_dicts"),
        ("Explain for loops with an example.", "for_loops"),
        ("What are functions in Python?", "functions_params"),
        ("What is the difference between == and =?", "equals_vs_assign"),
        ("Explain classes and objects.", "classes_objects"),
        ("What is exception handling?", "exception_handling"),
        ("What is a Python module?", "modules_packages"),
        ("Explain list comprehensions.", "list_comprehensions"),
        ("What is the difference between a list and a set?", "lists_vs_sets"),
        ("How do I read a text file in Python?", "file_handling")
    ]

    for question, expected_topic_id in sample_questions:
        res = client.post(
            "/api/chat/ask",
            cookies=cookies,
            headers={"X-CSRF-Token": csrf_token},
            json={"question": question}
        )
        assert res.status_code == 200, f"Failed for question: {question}"
        data = res.json()
        assert data["bot_message"]["is_supported"] is True
        assert data["bot_message"]["topic_id"] == expected_topic_id
        assert len(data["bot_message"]["content"]) > 30
        assert data["bot_message"]["code_example"] is not None
        assert data["bot_message"]["expected_output"] is not None

def test_chat_phrased_variations(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    variations = [
        "Can you explain how for loop works in python?",
        "difference between single equal and double equal",
        "how to read text files with open context manager",
        "lambda expressions anonymous function"
    ]

    for q in variations:
        res = client.post(
            "/api/chat/ask",
            cookies=cookies,
            headers={"X-CSRF-Token": csrf_token},
            json={"question": q}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["bot_message"]["is_supported"] is True
        assert data["bot_message"]["code_example"] is not None

def test_chat_unsupported_question_fallback(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    unsupported_query = "How to bake a chocolate vanilla cake?"
    res = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf_token},
        json={"question": unsupported_query}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["bot_message"]["is_supported"] is False
    assert data["bot_message"]["topic_id"] is None
    assert "not available in my current Python knowledge base" in data["bot_message"]["content"]
    assert len(data["related_topics"]) > 0

def test_chat_empty_and_oversized_validation(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    # Empty question
    res_empty = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf_token},
        json={"question": "   "}
    )
    assert res_empty.status_code == 422

    # Oversized question (> the backend's 4000-character limit)
    oversized = "a" * 4005
    res_over = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": csrf_token},
        json={"question": oversized}
    )
    assert res_over.status_code == 422

def test_browse_topics_endpoint(client: TestClient):
    res = client.get("/api/chat/topics")
    assert res.status_code == 200
    topics = res.json()
    assert isinstance(topics, list)
    assert len(topics) >= 25
    assert any(t["id"] == "python_intro" for t in topics)

def test_audit_regression_edge_cases(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    edge_cases = [
        ("Why should I use Python?", "python_intro"),
        ("How to convert string to integer?", "type_conversion"),
        ("What is the difference between is and ==?", "is_vs_equals"),
        ("What are return values and None?", "return_values")
    ]

    for question, expected_topic_id in edge_cases:
        res = client.post(
            "/api/chat/ask",
            cookies=cookies,
            headers={"X-CSRF-Token": csrf_token},
            json={"question": question}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["bot_message"]["is_supported"] is True
        assert data["bot_message"]["topic_id"] == expected_topic_id, f"Expected {expected_topic_id}, got {data['bot_message']['topic_id']} for '{question}'"

def test_audit_misleading_keywords(client: TestClient, registered_user):
    cookies = registered_user["cookies"]
    csrf_token = cookies.get("pyassist_csrf", "")

    misleading_questions = [
        "I love python but I want to buy a car",
        "is python good for making pasta?",
        "Tell me about JavaScript React components"
    ]

    for q in misleading_questions:
        res = client.post(
            "/api/chat/ask",
            cookies=cookies,
            headers={"X-CSRF-Token": csrf_token},
            json={"question": q}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["bot_message"]["is_supported"] is False
        assert data["bot_message"]["topic_id"] is None
