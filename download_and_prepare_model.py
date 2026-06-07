import os
from huggingface_hub import snapshot_download

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Repository with the medium checkpoint
REPO_ID = "Systran/faster-whisper-medium"

# Root directory used by ModelManager (download_root). We place the model
# under <ROOT>/Systran/faster-whisper-medium/ which matches the expected layout.
CACHE_ROOT = os.path.abspath("./models")
TARGET_DIR = os.path.join(CACHE_ROOT, "Systran", "faster-whisper-medium")

# Ensure the target parent directories exist
os.makedirs(TARGET_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
print(f"Downloading {REPO_ID} into {TARGET_DIR} …")
# snapshot_download will create a sub‑folder inside CACHE_ROOT that mirrors the repo name.
# Setting `local_dir` forces the final files to be placed exactly in TARGET_DIR.
local_path = snapshot_download(
    repo_id=REPO_ID,
    cache_dir=CACHE_ROOT,          # where HF stores its cache metadata
    local_dir=TARGET_DIR,          # exact location for the model files
    token=os.getenv("HF_TOKEN"),  # token must be exported in the shell
    resume_download=True,
    force_download=False,
)
print("Download complete.")
print(f"Model files are now in: {local_path}")

# ---------------------------------------------------------------------------
# Verify required files exist
# ---------------------------------------------------------------------------
required = ["config.json", "tokenizer.json", "vocab.txt", "model.bin"]
missing = [f for f in required if not os.path.isfile(os.path.join(TARGET_DIR, f))]
if missing:
    print("⚠️  Missing files:", missing)
else:
    print("✅ All required model files are present.")
