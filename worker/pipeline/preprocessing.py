import subprocess
import wave
from pathlib import Path
import webrtcvad
import os

def _run_ffmpeg(in_path: Path, out_path: Path) -> None:
    """Resample input audio to 16 kHz mono PCM wav using ffmpeg.
    The function raises if ffmpeg fails.
    """
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i",
        str(in_path),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

def _apply_vad(wav_path: Path) -> Path:
    """Apply webrtc VAD to a 16 kHz PCM wav file and return a new wav containing only speech frames.
    Returns the path to the filtered wav file.
    """
    vad = webrtcvad.Vad(2)  # aggressiveness 0-3 (2 is a balanced value)
    with wave.open(str(wav_path), "rb") as wf:
        sample_rate = wf.getframerate()
        if sample_rate != 16000:
            raise ValueError("VAD expects 16kHz audio")
        frames = wf.readframes(wf.getnframes())
        samp_width = wf.getsampwidth()
        n_channels = wf.getnchannels()
        if samp_width != 2 or n_channels != 1:
            raise ValueError("VAD expects 16-bit mono PCM wav")
    # 30 ms frame size in bytes (16‑bit = 2 bytes per sample)
    frame_duration_ms = 30
    frame_size = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    speech_frames = []
    for i in range(0, len(frames), frame_size):
        frame = frames[i : i + frame_size]
        if len(frame) < frame_size:
            break
        if vad.is_speech(frame, sample_rate):
            speech_frames.append(frame)
    filtered_path = wav_path.with_name(wav_path.stem + "_filtered.wav")
    with wave.open(str(filtered_path), "wb") as out_wf:
        out_wf.setnchannels(1)
        out_wf.setsampwidth(2)
        out_wf.setframerate(sample_rate)
        for f in speech_frames:
            out_wf.writeframes(f)
    return filtered_path

def preprocess_audio(audio_path: Path) -> Path:
    """Full preprocessing pipeline:
    1️⃣ Resample to 16 kHz mono wav using ffmpeg.
    2️⃣ Apply webrtc VAD to drop non‑speech segments.
    Returns the path to the final wav ready for Faster‑Whisper.
    """
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    # Step 1: resample
    resampled_path = audio_path.with_name(audio_path.stem + "_16k.wav")
    _run_ffmpeg(audio_path, resampled_path)
    # Step 2: VAD filtering
    filtered_path = _apply_vad(resampled_path)
    # Clean up intermediate resampled file
    try:
        os.remove(resampled_path)
    except OSError:
        pass
    return filtered_path
