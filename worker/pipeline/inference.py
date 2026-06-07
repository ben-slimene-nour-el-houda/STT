def run_inference(model_manager, audio_path):
    """Run Faster‑Whisper transcription and return the concatenated text.
    model_manager is an instance of ModelManager (singleton).
    """
    # Faster‑Whisper returns a tuple (segments, info)
    result, _ = model_manager.transcribe(str(audio_path), language="ar")
    # Concatenate segment texts preserving order
    texts = [segment.text for segment in result]
    return " ".join(texts).strip()
