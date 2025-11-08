# Project Overview

## Robotic Face Recognition and Emotion Analysis System

This project is a real-time face recognition and emotion analysis system built with Python, Flask, DeepFace and MediaPipe. It is designed to monitor a webcam feed, analyze faces for emotions, detect and record "dangerous" individuals (based on configured emotion thresholds), and provide a web interface and REST API for monitoring and control.

### Key Capabilities
- Real-time face detection and face-mesh overlay (MediaPipe)
- Emotion analysis for 7 standard emotion categories (DeepFace)
- Face embedding extraction and cosine-similarity-based recognition
- Automatic registration and persistent storage of detected dangerous persons
- Web interface (Flask) with an MJPEG video stream and REST endpoints

### Intended Use Cases
- Security and surveillance monitoring
- Emotion research and human behavior analytics
- Access control with emotion-awareness
- Prototyping and education for computer vision tasks

---

## High-level Architecture

- Client (browser): fetches the `/` template and displays MJPEG stream from `/video_feed`. It can query `/status`, `/current_emotions`, and `/captured` for information.
- Server (Flask `main.py`): exposes the routes, loads modules, and orchestrates camera and analysis.
- Modules: `modules/camera.py` (streaming), `modules/face_analysis.py` (DeepFace operations), `modules/storage.py` (file I/O & persistence), `modules/config.py` (centralized configuration and state).
- Models/Libs: DeepFace, MediaPipe, OpenCV, NumPy.

---

## Files created in this documentation
- `docs/PROJECT_OVERVIEW.md` (this file)
- `docs/MODULE_DOCUMENTATION.md` (detailed function-level docs)
- `docs/API_REFERENCE.md` (API endpoints, request/response examples)
- `docs/DEPLOYMENT_GUIDE.md` (installation, running, troubleshooting)
- `docs/README.md` (index linking the above)


Last updated: November 8, 2025
