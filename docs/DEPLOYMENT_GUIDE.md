# Deployment Guide

This guide covers local setup, virtual environment, dependency installation, running the app, and common troubleshooting steps.

## Requirements
- Python 3.10.x (recommended)
- Webcam for live testing (or a virtual camera)
- 4GB RAM minimum, 8GB recommended for comfortable operation
- Internet connection for model downloads on first run

## 1) Clone repository

```bash
git clone <your-repo-url>
cd robotic-lesson-project
```

## 2) Create and activate virtual environment (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
# If execution policy blocks, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 3) Install dependencies

```bash
pip install -r requirements.txt
```

Notes:
- `requirements.txt` includes TensorFlow and PyTorch; install time and disk usage are significant.
- If you have problems with binary packages on Windows, consider using a preconfigured Python distribution (Anaconda) or matching wheel files.

## 4) Run the application

```bash
python main.py
```

Open browser:
- Local: `http://localhost:5000`

## 5) Common issues and fixes

- "No module named tensorflow":
  - `pip install tensorflow==2.12.0`
- Camera not found:
  - Change camera index in `modules/camera.py`: `cv2.VideoCapture(0)` → try `1`, `2`, ...
- Model download failures:
  - Ensure you have a working internet connection; DeepFace will download model files the first time.
- DLL load errors on Windows:
  - Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

## 6) Production recommendations
- Run behind a WSGI server (Gunicorn / uWSGI) and a reverse proxy (Nginx).
- Enable HTTPS with a valid certificate.
- Move persistence to a DB for concurrency and reliability.
- Add authentication for the web UI and API endpoints.

## 7) Scaling and optimization tips
- Lower camera resolution to reduce CPU load.
- Increase `ANALYSIS_INTERVAL` in `modules/config.py` to analyze less frequently.
- Use GPU-enabled TensorFlow build and CUDA drivers for faster inference.

End of deployment guide.
