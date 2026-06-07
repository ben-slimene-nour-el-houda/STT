# download_tiny_model.py
# ------------------------------------------------------------
# Download the Faster‑Whisper **tiny** checkpoint and place it
# where ModelManager (download_root="./models") expects it.
# ------------------------------------------------------------
import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
REPO_ID = "Systran/faster-whisper-tiny"          # tiny checkpoint (~30 MB)
CACHE_ROOT = Path(os.getenv("MODEL_DIR", "./models"))  # same as ModelManager
TARGET_DIR = CACHE_ROOT / "Systran" / "faster-whisper-tiny"

# Files that Faster‑Whisper needs (exact names)
REQUIRED_FILES = [
    "config.json",
    "tokenizer.json",
    "model.bin",
]

def main() -> None:
    # Ensure the target directory exists
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # Use the token from the environment (export HF_TOKEN=… before running)
    token = os.getenv("HF_TOKEN")
    if not token:
        print(
            "⚠️  No HF_TOKEN found in environment – downloads will be unauthenticated "
            "(slower and rate‑limited).",
            file=sys.stderr,
        )

    print(f"Downloading {REPO_ID} into {TARGET_DIR} …")
    try:
        # `snapshot_download` creates the correct sub‑folder structure.
        # By passing `local_dir=TARGET_DIR` we force the files to land exactly there.
        snapshot_download(
            repo_id=REPO_ID,
            cache_dir=str(CACHE_ROOT),
            local_dir=str(TARGET_DIR),   # exact location for model files
            token=token,
            resume_download=True,
            force_download=False,
        )
    except Exception as exc:
        print(f"❌ Failed to download model: {exc}", file=sys.stderr)
        sys.exit(1)

    # Verify that all required files are present
    missing = [f for f in REQUIRED_FILES if not (TARGET_DIR / f).is_file()]
    if missing:
        print(f"⚠️  Missing files after download: {missing}", file=sys.stderr)
        sys.exit(1)

    print("✅ All required model files are present.")
    print(f"Model ready at: {TARGET_DIR}")

if __name__ == "__main__":
    main()
