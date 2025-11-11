"""
Configuration constants and global settings
"""
import os

# Directory configuration
CAPTURE_DIR = "static/captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Analysis parameters
ANALYSIS_INTERVAL = 3     # analyze every 3 frames (daha sık analiz için optimize edildi)
HISTORY_SIZE = 5           # average of last 5 analyses (daha fazla smoothing)
DANGER_THRESHOLD = 70     # danger threshold (angry+fear+disgust sum)
FACE_SIMILARITY_THRESHOLD = 0.6  # face similarity threshold (0-1 range, lower=stricter)

# Emotion analysis optimization
EMOTION_CONFIDENCE_THRESHOLD = 35.0  # minimum emotion confidence to consider valid (%)

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

# ESP32 Camera optimal settings for emotion analysis
ESP_OPTIMAL_SETTINGS = {
    "framesize": 8,        # XGA (1024x768) - optimal balance
    "quality": 10,         # Best JPEG quality
    "brightness": 0,       # Default brightness
    "contrast": 0,         # Default contrast
    "saturation": 0,       # Natural saturation for skin tone
    "gainceiling": 2,      # Moderate gain ceiling (reduce noise)
    "awb": 1,             # Auto White Balance ON (critical!)
    "awb_gain": 1,        # AWB gain ON
    "aec": 1,             # Auto Exposure ON
    "aec2": 1,            # DSP exposure ON
    "ae_level": 0,        # Default AE level
    "agc": 1,             # Auto Gain ON
    "bpc": 1,             # Black pixel correction ON
    "wpc": 1,             # White pixel correction ON
    "raw_gma": 1,         # Raw gamma ON
    "lenc": 1,            # Lens correction ON
    "hmirror": 0,         # No horizontal mirror
    "vflip": 0,           # No vertical flip
    "dcw": 1,             # Downsize enable
    "face_detect": 1,     # Face detection ON
}

# ESP32 Resolution options
ESP_FRAMESIZE_OPTIONS = {
    "UXGA": 10,    # 1600x1200
    "SXGA": 9,     # 1280x1024
    "XGA": 8,      # 1024x768 (optimal for emotion analysis)
    "SVGA": 7,     # 800x600
    "VGA": 6,      # 640x480
    "CIF": 5,      # 352x288
    "QVGA": 4,     # 320x240
    "QCIF": 3,     # 176x144
    "HQVGA": 2,    # 240x176
    "QQVGA": 1,    # 160x120
}
