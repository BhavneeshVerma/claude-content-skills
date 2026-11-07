# Launcher for tag-images.py. Keeps the package cache on D: for this run only (no system settings changed).
$env:UV_CACHE_DIR = "D:\dev-cache\uv"
$env:PYTHONIOENCODING = "utf-8"
uv run --python 3.12 --with google-genai --with pillow python -I "$PSScriptRoot\tag-images.py" @args
