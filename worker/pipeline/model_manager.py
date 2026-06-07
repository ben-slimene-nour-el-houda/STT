import os
import torch
from faster_whisper import WhisperModel
from common.settings import settings

class ModelManager:
    """Singleton that loads the Faster‑Whisper model once per worker process.
    Supports automatic GPU detection via torch.cuda.is_available().
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Determine device: "auto" will select CUDA if available, otherwise CPU.
            if settings.MODEL_DEVICE.lower() == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = settings.MODEL_DEVICE.lower()
            compute_type = "float16" if device == "cuda" else "int8"
            # Load from the explicit local directory where we downloaded it
            local_model_path = os.path.abspath(os.path.join(os.getenv("MODEL_DIR", "./models"), "Systran", "faster-whisper-tiny"))
            cls._instance.model = WhisperModel(
                local_model_path,
                device=device,
                compute_type=compute_type,
            )
        return cls._instance

    def transcribe(self, audio_path: str, language: str | None = None):
        """Run Faster‑Whisper transcription.
        Returns the raw Faster‑Whisper result (segments, info).
        """
        return self.model.transcribe(audio_path, language=language)

def get_model_manager():
    """Convenient accessor used by the Celery task."""
    return ModelManager()
