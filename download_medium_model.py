import os
from huggingface_hub import snapshot_download

# Define where the model should be cached (matches ModelManager's download_root)
CACHE_ROOT = os.path.abspath("./models")

# The repository identifier for the medium checkpoint
REPO_ID = "Systran/faster-whisper-medium"

print(f"Downloading {REPO_ID} into {CACHE_ROOT} ...")

# snapshot_download will create the correct subdirectory structure under CACHE_ROOT
snapshot_download(
    repo_id=REPO_ID,
    cache_dir=CACHE_ROOT,
    local_dir=CACHE_ROOT,  # force exact location
    token=os.getenv("HF_TOKEN"),
    resume_download=True,
    force_download=False,
    local_files_only=False,
)

print("Download complete.")
