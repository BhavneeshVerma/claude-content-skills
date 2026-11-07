# Launcher for dissect.py. Keeps the package cache and model downloads on D: for this run only (no system settings changed).
$env:UV_CACHE_DIR = "D:\dev-cache\uv"
$env:HF_HOME = "D:\dev-cache\huggingface"
$env:PYTHONIOENCODING = "utf-8"
uv run --python 3.12 --with yt-dlp --with imageio-ffmpeg --with "scenedetect[opencv-headless]" --with google-genai --with faster-whisper python -I "$PSScriptRoot\dissect.py" @args
