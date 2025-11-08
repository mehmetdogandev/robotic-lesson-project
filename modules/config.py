"""
Yapılandırma sabitleri ve global ayarlar
"""
import os

# Dizin yapılandırması
CAPTURE_DIR = "static/captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Analiz parametreleri
ANALYSIS_INTERVAL = 5     # her 5 karede bir analiz yap
HISTORY_SIZE = 3           # son 3 analizin ortalamasını al
DANGER_THRESHOLD = 70     # tehlike eşiği (angry+fear+disgust toplamı)
FACE_SIMILARITY_THRESHOLD = 0.6  # Yüz benzerlik eşiği (0-1 arası, düşük=daha sıkı)

# Algılama durumu
DETECTION_ENABLED = True

# Duygu etiketleri (Türkçe)
emotion_labels = {
    "happy": "Mutlu",
    "sad": "Uzgun",
    "angry": "Kizgin",
    "surprise": "Sasirmis",
    "fear": "Korkmus",
    "disgust": "Tiksinmi",
    "neutral": "Notr"
}

# Son durum verisi
latest_state = {
    "timestamp": None,
    "emotions": None,
    "main_emotion": None,
    "danger_score": 0.0,
}
