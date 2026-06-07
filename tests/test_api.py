import os
import json
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch

# Ensure the project root is on PYTHONPATH
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.main import app
from worker.tasks import transcribe_task

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_transcribe_endpoint_and_status(monkeypatch):
    # Mock the Celery task to avoid real processing
    dummy_task_id = str(uuid.uuid4())
    dummy_result = {"transcription": "hello world", "source_file": "dummy.wav"}

    class DummyAsyncResult:
        def __init__(self, task_id):
            self.id = task_id
            self.status = "SUCCESS"
            self.result = json.dumps(dummy_result)

    def mock_send_task(name, args=None, kwargs=None):
        # args expected: [task_id, file_path]
        return DummyAsyncResult(args[0])

    # Patch Celery app send_task
    monkeypatch.setattr("worker.celery_app.celery_app.send_task", mock_send_task)

    # Call the transcribe endpoint
    files = {"file": ("test.wav", b"fake wav content")}
    response = client.post("/transcribe", files=files, headers={"X-API-KEY": "testkey"})
    assert response.status_code == 200
    payload = response.json()
    assert "task_id" in payload
    task_id = payload["task_id"]

    # Query status endpoint
    status_resp = client.get(f"/status/{task_id}", headers={"X-API-KEY": "testkey"})
    assert status_resp.status_code == 200
    status_json = status_resp.json()
    assert status_json["status"] == "SUCCESS"
    assert json.loads(status_json["result"]) == dummy_result
