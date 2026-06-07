from celery import shared_task
from pathlib import Path
import json

from .pipeline.preprocessing import preprocess_audio
from .pipeline.model_manager import get_model_manager
from .pipeline.inference import run_inference
from .pipeline.postprocessing import postprocess_text
from .pipeline.optional_llm import enrich_with_llm
from common.settings import settings
from common.logger import get_logger

logger = get_logger("worker")

@shared_task(name="worker.tasks.transcribe_task")
def transcribe_task(task_id: str, file_path: str):
    """Celery task that runs the full STT pipeline.

    Args:
        file_path: Absolute path to the uploaded audio file.
    Returns:
        JSON string with transcription and metadata.
    """
    try:
        logger.info("Starting transcription", file_path=file_path)
        # 1️⃣ Pre‑processing (resample, denoise, VAD)
        processed_path = preprocess_audio(Path(file_path))
        # 2️⃣ Model inference
        model_manager = get_model_manager()
        raw_result = run_inference(model_manager, processed_path)
        # 3️⃣ Post‑processing (punctuation, normalization)
        cleaned_text = postprocess_text(raw_result)
        # 4️⃣ Optional LLM enrichment
        final_text = enrich_with_llm(cleaned_text) if settings.ENABLE_LLM else cleaned_text
        # 5️⃣ Return result
        result = {"transcription": final_text, "source_file": file_path}
        logger.info("Transcription completed", file_path=file_path)
        return result
    except Exception as e:
        logger.exception("Transcription failed", error=str(e))
        raise
