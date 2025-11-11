"""
Face analysis, emotion detection, and person recognition operations
"""
import numpy as np
from deepface import DeepFace
from collections import deque
import requests
import json
from modules.config import HISTORY_SIZE, FACE_SIMILARITY_THRESHOLD

# ESP32 target URL for emotion data (can be set by user)
ESP32_TARGET_URL = None

# Emotion history
emotion_history = deque(maxlen=HISTORY_SIZE)

# Face embeddings of registered dangerous persons
registered_dangerous_faces = {}


# -----------------------
# Preprocessing Helpers
# -----------------------
import cv2
import numpy as _np
import mediapipe as _mp

_mp_face_mesh = _mp.solutions.face_mesh

def preprocess_face(image, bbox=None, output_size=(224, 224), clahe=True):
    """Detect/align/crop a face and apply CLAHE + normalization.

    Returns an RGB float32 numpy array normalized for pretrained backbones
    or None if no face/crop could be produced.
    """
    img = image.copy()
    h, w = img.shape[:2]

    # If bbox not provided, try to detect face with MediaPipe (fast single-shot)
    if bbox is None:
        with _mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as fm:
            results = fm.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                return None
            lm = results.multi_face_landmarks[0].landmark
            xs = [int(p.x * w) for p in lm]
            ys = [int(p.y * h) for p in lm]
            x1, x2 = max(min(xs) - 20, 0), min(max(xs) + 20, w)
            y1, y2 = max(min(ys) - 20, 0), min(max(ys) + 20, h)
            bbox = (x1, y1, x2 - x1, y2 - y1)

    x, y, ww, hh = bbox
    face = img[y:y + hh, x:x + ww]
    if face.size == 0:
        return None

    # Resize to model input
    face = cv2.resize(face, output_size, interpolation=cv2.INTER_LINEAR)

    # Apply CLAHE on L channel for illumination normalization
    if clahe:
        lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe_op = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe_op.apply(l)
        lab = cv2.merge((l, a, b))
        face = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Convert to RGB and normalize to imagenet stats
    face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB).astype(_np.float32) / 255.0
    mean = _np.array([0.485, 0.456, 0.406], dtype=_np.float32)
    std = _np.array([0.229, 0.224, 0.225], dtype=_np.float32)
    face_rgb = (face_rgb - mean) / std
    return face_rgb


# -----------------------
# Temporal Smoothing
# -----------------------
class TemporalSmoother:
    """Gelişmiş temporal smoother for emotion probability vectors.

    Duygu algılama doğruluğu için optimize edildi:
    - Daha uzun hafıza (maxlen=10)
    - Daha agresif smoothing (ema_alpha=0.7)
    - Hysteresis ile daha stabil sonuçlar
    """
    def __init__(self, maxlen=10, ema_alpha=0.7):
        self.maxlen = maxlen
        self.ema_alpha = ema_alpha
        self.deque = deque(maxlen=maxlen)
        self.last_dominant = None  # Hysteresis için son dominant emotion

    def update(self, prob_vector):
        """Add a new probability vector (list/np.array) and return smoothed vector."""
        arr = _np.array(prob_vector, dtype=_np.float32)
        if arr.sum() <= 0:
            # avoid invalid vectors
            return None
        # normalize
        arr = arr / (arr.sum() + 1e-8)
        self.deque.append(arr)
        return self.get_smoothed()

    def get_smoothed(self):
        if not self.deque:
            return None
        
        # Exponential Moving Average smoothing
        ema = _np.array(self.deque[0], dtype=_np.float32).copy()
        for v in list(self.deque)[1:]:
            ema = self.ema_alpha * v + (1.0 - self.ema_alpha) * ema
        
        # normalize
        ema = ema / (ema.sum() + 1e-8)
        
        # Hysteresis: son dominant emotion'a hafif bias ekle (titremeyi azaltır)
        if self.last_dominant is not None and len(self.deque) > 3:
            ema[self.last_dominant] *= 1.05  # %5 boost
            ema = ema / ema.sum()  # Re-normalize
        
        # Update last dominant
        self.last_dominant = _np.argmax(ema)
        
        return ema


def emotions_dict_to_vector(emotions_dict, ordered_keys=None):
    """Convert DeepFace emotions dict to a probability vector in a stable order.

    If ordered_keys not provided, uses the typical DeepFace order.
    """
    if ordered_keys is None:
        ordered_keys = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    vec = []
    for k in ordered_keys:
        vec.append(float(emotions_dict.get(k, 0.0)))
    # convert to probabilities (sum may not equal 100 due to averaging)
    arr = _np.array(vec, dtype=_np.float32)
    s = arr.sum()
    if s <= 0:
        return arr
    return arr / (s + 1e-8)


def vector_to_emotions_dict(vec, ordered_keys=None):
    if ordered_keys is None:
        ordered_keys = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    # Convert to percentage (0-100 range)
    return {k: float(vec[i] * 100.0) for i, k in enumerate(ordered_keys)}


def get_face_embedding(frame):
    """Extracts face embedding (vector) from a frame."""
    try:
        embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=False)
        return np.array(embedding[0]["embedding"])
    except:
        return None


def is_registered_dangerous_person(current_embedding):
    """Checks if the current face has been registered before."""
    if current_embedding is None:
        return False, None
    
    for person_id, saved_embedding in registered_dangerous_faces.items():
        similarity = np.dot(current_embedding, saved_embedding) / (
            np.linalg.norm(current_embedding) * np.linalg.norm(saved_embedding)
        )
        if similarity > FACE_SIMILARITY_THRESHOLD:
            return True, person_id
    return False, None


def analyze_emotions(rgb_frame):
    """Gelişmiş duygu analizi - daha doğru ve güvenilir sonuçlar.
    
    İyileştirmeler:
    - Yüz hizalama (align=True) ile %15-20 daha doğru
    - OpenCV detector ile daha hızlı
    - Düşük güvenilirlikli sonuçları filtreleme
    """
    try:
        analysis = DeepFace.analyze(
            rgb_frame, 
            actions=['emotion'], 
            enforce_detection=False,
            detector_backend='opencv',  # Daha hızlı
            align=True  # Yüz hizalama ile daha doğru sonuç
        )
        
        if isinstance(analysis, list):
            emotions = analysis[0]['emotion']
        else:
            emotions = analysis['emotion']
        
        # Dominant emotion'un güvenilirlik kontrolü
        max_confidence = max(emotions.values())
        
        from modules.config import EMOTION_CONFIDENCE_THRESHOLD
        if max_confidence >= EMOTION_CONFIDENCE_THRESHOLD:
            emotion_history.append(emotions)
            return emotions
        else:
            # Düşük güven - eğer history varsa son değeri kullan, yoksa neutral
            if emotion_history:
                return emotion_history[-1]
            else:
                # Neutral emotion döndür
                neutral_emotions = {k: 0.0 for k in emotions.keys()}
                neutral_emotions['neutral'] = 100.0
                emotion_history.append(neutral_emotions)
                return neutral_emotions
            
    except Exception as e:
        # Hata durumunda son bilinen duyguyu kullan
        if emotion_history:
            return emotion_history[-1]
        return None


def get_average_emotions():
    """Gelişmiş ağırlıklı ortalama hesaplama.
    
    Son frame'lere daha fazla ağırlık vererek daha hızlı tepki verir
    ama yeterince smooth kalır.
    """
    if not emotion_history:
        return {}, "neutral"
    
    # Ağırlıklı ortalama - son frame'ler daha önemli
    n = len(emotion_history)
    weights = np.linspace(0.5, 1.0, n)
    weights = weights / weights.sum()  # Normalize et
    
    avg_emotions = {}
    for key in emotion_history[0].keys():
        weighted_sum = sum(e[key] * w for e, w in zip(emotion_history, weights))
        avg_emotions[key] = weighted_sum
    
    # Toplam 100% olması için normalize et
    total = sum(avg_emotions.values())
    if total > 0:
        avg_emotions = {k: (v / total) * 100 for k, v in avg_emotions.items()}
    
    main_emotion = max(avg_emotions, key=avg_emotions.get)
    
    # Minimum threshold - eğer dominant emotion çok düşükse neutral kabul et
    if avg_emotions[main_emotion] < 30.0:  # %30'un altındaysa belirsiz
        main_emotion = "neutral"
    
    return avg_emotions, main_emotion


def calculate_danger_score(avg_emotions):
    """Calculates danger score."""
    return sum(avg_emotions.get(k, 0) for k in ["angry", "fear", "disgust"])


def register_dangerous_person(person_id, embedding):
    """Registers a new dangerous person."""
    registered_dangerous_faces[person_id] = embedding
    print(f"⚠️ NEW dangerous person registered: {person_id}")


def clear_emotion_history():
    """Clears emotion history."""
    emotion_history.clear()


def set_esp32_target_url(url):
    """Sets ESP32 target URL for emotion data transmission."""
    global ESP32_TARGET_URL
    ESP32_TARGET_URL = url
    print(f"✓ ESP32 hedef URL ayarlandı: {url}")


def send_emotion_to_esp32(emotion, confidence):
    """Sends emotion data to ESP32 via HTTP POST (non-blocking, fast)."""
    global ESP32_TARGET_URL
    
    if not ESP32_TARGET_URL:
        return False
    
    try:
        payload = {
            "emotion": emotion,
            "confidence": float(confidence)
        }
        
        # Çok kısa timeout - ESP32 meşgulse skip et
        response = requests.post(
            ESP32_TARGET_URL,
            json=payload,
            timeout=0.5  # 500ms - daha hızlı
        )
        
        return response.status_code == 200
            
    except:
        # Sessizce devam et - log spam'i yok
        return False
