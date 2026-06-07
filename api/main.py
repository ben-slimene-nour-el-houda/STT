from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid, shutil
from pathlib import Path

from common.settings import settings
from common.logger import get_logger
from api.auth import get_api_key
from worker.celery_app import celery_app

import json
logger = get_logger("api")
app = FastAPI(title="Speech-to-Text API Gateway", version="1.0.0")

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Simple rate limiter using Redis token bucket
from redis import Redis
redis_client = Redis.from_url(settings.REDIS_URL)

def rate_limit(api_key: str = Depends(get_api_key)):
    """Simple token bucket rate limiting using Redis.
    If Redis is unavailable, skip rate limiting.
    """
    token_key = f"rate_limit:{api_key}"
    try:
        tokens = redis_client.get(token_key)
        if tokens is None:
            redis_client.set(token_key, settings.RATE_LIMIT_TOKENS - 1, ex=settings.RATE_LIMIT_INTERVAL)
            return
        tokens = int(tokens)
        if tokens <= 0:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        redis_client.decr(token_key)
    except Exception:
        # Redis not reachable – allow request to proceed.
        return
    token_key = f"rate_limit:{api_key}"
    tokens = redis_client.get(token_key)
    if tokens is None:
        redis_client.set(token_key, settings.RATE_LIMIT_TOKENS - 1, ex=settings.RATE_LIMIT_INTERVAL)
        return
    tokens = int(tokens)
    if tokens <= 0:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    redis_client.decr(token_key)
    return

class TranscribeResponse(BaseModel):
    task_id: str
    detail: str = "Transcription task submitted"

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit),
):
    task_id = str(uuid.uuid4())
    file_path = Path(settings.UPLOAD_DIR) / f"{task_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info("Received file", task_id=task_id, filename=file.filename)
    # Enqueue Celery task
    celery_app.send_task("worker.tasks.transcribe_task", args=[task_id, str(file_path)], task_id=task_id)
    return TranscribeResponse(task_id=task_id)

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status/{task_id}", response_model=TaskStatusResponse)
def get_status(task_id: str, api_key: str = Depends(get_api_key)):
    from celery.result import AsyncResult
    try:
        result = AsyncResult(task_id, app=celery_app)
        status = result.status
        # Celery stores the task return value as is; our task returns a JSON string.
        payload = result.result if status == "SUCCESS" else None
    except Exception as exc:
        # If the backend (Redis) is unreachable we raise a clear error instead of faking a success.
        raise HTTPException(status_code=503, detail="Result backend unavailable") from exc
    return TaskStatusResponse(task_id=task_id, status=status, result=payload)
from fastapi.responses import HTMLResponse

@app.get("/transcribe_html/{task_id}", response_class=HTMLResponse)
def transcribe_html(task_id: str, api_key: str = Depends(get_api_key)):
    """Render the transcription in an HTML page with RTL direction.
    Useful for visual inspection when the terminal does not render Arabic correctly.
    """
    # Re‑use the existing status logic
    from fastapi import Request
    status_resp = get_status(task_id, api_key)
    if status_resp.status != "SUCCESS":
        raise HTTPException(status_code=202, detail="Result not ready")
    # Extract transcription string; it may be a dict or a raw JSON string
    transcription = ""
    if isinstance(status_resp.result, dict):
        transcription = status_resp.result.get("transcription", "")
    elif isinstance(status_resp.result, str):
        try:
            import json as _json
            transcription = _json.loads(status_resp.result).get("transcription", "")
        except Exception:
            transcription = status_resp.result
    html_content = f"""<!DOCTYPE html>
<html lang=\"ar\" dir=\"rtl\">
<head>
    <meta charset=\"UTF-8\" />
    <title>Transcription Result</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; background: #f9f9f9; padding: 2rem; }}
        .result {{ font-size: 1.5rem; direction: rtl; text-align: right; background: #fff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class=\"result\">{transcription}</div>
</body>
</html>"""
    return HTMLResponse(content=html_content)
