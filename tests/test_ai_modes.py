"""Route and mode-instruction checks; Gemini provider calls are mocked."""
import asyncio

import pytest
from fastapi.testclient import TestClient

from pyassist.app.config import settings
from pyassist.app.gemini_service import MODE_PROMPTS
from pyassist.app.routes import chat as chat_routes
from pyassist.app import gemini_service


MODE_QUESTIONS = [
    ("ask", "What is the difference between == and is in Python?"),
    ("generate", "Write a Python program to check whether a number is prime. Include sample input and output."),
    ("debug", "Why does numbers = [1, 2]; print(numbers[2]) raise an error? Provide corrected code."),
    ("explain", "Explain this code step by step: for i in range(3): print(i)"),
    ("review", "Review this code for security and correctness: password = input(); query = 'SELECT * FROM users WHERE name=' + password"),
]


@pytest.fixture(autouse=True)
def disable_live_gemini(monkeypatch):
    """Keep tests offline unless an individual test explicitly mocks the provider."""
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)


@pytest.mark.parametrize("mode,question", MODE_QUESTIONS)
def test_authenticated_chat_route_passes_selected_mode_to_gemini(
    client: TestClient, registered_user, monkeypatch, mode, question
):
    captured = {}

    async def fake_gemini_response(prompt, mode="ask", preferred_model=None):
        captured.update(prompt=prompt, mode=mode)
        return {
            "success": True,
            "content": f"Mock Gemini response for {mode}: relevant Python guidance.",
            "code_example": "print('verified')",
            "expected_output": "verified",
            "model_used": "unit-test-model",
        }

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-placeholder")
    monkeypatch.setattr(chat_routes, "generate_gemini_response", fake_gemini_response)
    cookies = registered_user["cookies"]
    response = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": cookies.get("pyassist_csrf", "")},
        json={"question": question, "mode": mode},
    )

    assert response.status_code == 200
    data = response.json()
    assert captured == {"prompt": question, "mode": mode}
    assert data["mode"] == mode
    assert data["bot_message"]["mode"] == mode
    assert data["bot_message"]["model_used"] == "unit-test-model"
    assert data["bot_message"]["topic_id"] == f"gemini_{mode}"
    assert "Mock Gemini response" in data["bot_message"]["content"]


@pytest.mark.parametrize("mode,question", MODE_QUESTIONS)
def test_each_mode_uses_its_own_google_genai_instruction(monkeypatch, mode, question):
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return type("FakeResponse", (), {"text": "Mode-specific test response."})()

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "unit-test-placeholder"
            self.models = FakeModels()

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-placeholder")
    monkeypatch.setattr(gemini_service.genai, "Client", FakeClient)

    content, model = gemini_service._call_gemini_sync(question, mode, "unit-test-model")

    assert content == "Mode-specific test response."
    assert model == "unit-test-model"
    assert captured["model"] == "unit-test-model"
    assert captured["contents"] == question
    assert captured["config"]["system_instruction"] == MODE_PROMPTS[mode]


@pytest.mark.parametrize("mode,question", MODE_QUESTIONS[1:])
def test_non_ask_modes_are_not_mislabeled_as_knowledge_base_answers(
    client: TestClient, registered_user, mode, question
):
    cookies = registered_user["cookies"]
    response = client.post(
        "/api/chat/ask",
        cookies=cookies,
        headers={"X-CSRF-Token": cookies.get("pyassist_csrf", "")},
        json={"question": question, "mode": mode},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["bot_message"]["mode"] == mode
    assert data["bot_message"]["model_used"] is None
    assert data["bot_message"]["topic_id"] is None
    assert data["bot_message"]["is_supported"] is False
    assert "requires Gemini" in data["bot_message"]["content"]


def test_gemini_provider_failure_does_not_expose_raw_diagnostics(monkeypatch):
    def raise_provider_error(*args):
        raise RuntimeError("request failed with API_KEY=private-provider-detail")

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "unit-test-placeholder")
    monkeypatch.setattr(gemini_service, "_call_gemini_sync", raise_provider_error)
    result = asyncio.run(gemini_service.generate_gemini_response("test prompt", mode="ask"))

    assert result["success"] is False
    assert "private-provider-detail" not in result["message"]
    assert "API_KEY=" not in result["message"]
