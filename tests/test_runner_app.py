import importlib
import os

from fastapi.testclient import TestClient

from ariv.runner.app import app


def test_chat_streaming_response() -> None:
    os.environ["ARIV_MOCK_LLAMA"] = "1"
    client = TestClient(app)
    response = client.post(
        "/v1/chat",
        json={"user_id": "u1", "text": "hello world", "preferred_lang": "en", "task_hint": "code"},
    )
    assert response.status_code == 200
    text = response.text
    assert "metadata" in text


def test_registry_path_independent_of_cwd(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ARIV_MODELS_YAML", raising=False)
    monkeypatch.chdir(tmp_path)
    runner_module = importlib.import_module("ariv.runner.app")
    importlib.reload(runner_module)
    assert runner_module.registry.get("mock-0.1b-q4_0").name == "mock-0.1b-q4_0"
