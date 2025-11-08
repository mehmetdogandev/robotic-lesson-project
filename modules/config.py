"""
Configuration constants and global settings
"""
import os

# Directory configuration
CAPTURE_DIR = "static/captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Analysis parameters
ANALYSIS_INTERVAL = 5     # analyze every 5 frames
HISTORY_SIZE = 3           # average of last 3 analyses
DANGER_THRESHOLD = 70     # danger threshold (angry+fear+disgust sum)
FACE_SIMILARITY_THRESHOLD = 0.6  # face similarity threshold (0-1 range, lower=stricter)

# Detection status
DETECTION_ENABLED = True

# Emotion labels (Turkish)
emotion_labels = {
    "happy": "Mutlu",
    "sad": "Uzgun",
    "angry": "Kizgin",
    "surprise": "Sasirmis",
    "fear": "Korkmus",
    "disgust": "Tiksinmi",
    "neutral": "Notr"
}

# Latest state data
latest_state = {
    "timestamp": None,
    "emotions": None,
    "main_emotion": None,
    "danger_score": 0.0,
}
