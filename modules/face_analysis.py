"""
Yüz analizi, emotion detection ve kişi tanıma işlemleri
"""
import numpy as np
from deepface import DeepFace
from collections import deque
from modules.config import HISTORY_SIZE, FACE_SIMILARITY_THRESHOLD

# Emotion geçmişi
emotion_history = deque(maxlen=HISTORY_SIZE)

# Kayıtlı tehlikeli kişilerin yüz embeddingleri
registered_dangerous_faces = {}


def get_face_embedding(frame):
    """Bir frame'den yüz embedding'i (vektör) çıkarır."""
    try:
        embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=False)
        return np.array(embedding[0]["embedding"])
    except:
        return None


def is_registered_dangerous_person(current_embedding):
    """Mevcut yüzün daha önce kaydedilip kaydedilmediğini kontrol eder."""
    if current_embedding is None:
        return False, None
    
    for person_id, saved_embedding in registered_dangerous_faces.items():
        # Cosine similarity hesapla
        similarity = np.dot(current_embedding, saved_embedding) / (
            np.linalg.norm(current_embedding) * np.linalg.norm(saved_embedding)
        )
        
        if similarity > FACE_SIMILARITY_THRESHOLD:
            return True, person_id  
    
    return False, None


def analyze_emotions(rgb_frame):
    """Frame'den emotion analizi yapar ve geçmişe ekler."""
    try:
        analysis = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
        emotions = analysis[0]['emotion']
        emotion_history.append(emotions)
        return emotions
    except Exception as e:
        print("Analiz hatası:", e)
        return None


def get_average_emotions():
    """Emotion geçmişinden ortalama hesaplar."""
    if not emotion_history:
        return {}, "neutral"
    
    avg_emotions = {k: np.mean([e[k] for e in emotion_history]) for k in emotion_history[0].keys()}
    main_emotion = max(avg_emotions, key=avg_emotions.get)
    
    return avg_emotions, main_emotion


def calculate_danger_score(avg_emotions):
    """Tehlike skorunu hesaplar."""
    return sum(avg_emotions.get(k, 0) for k in ["angry", "fear", "disgust"])


def register_dangerous_person(person_id, embedding):
    """Yeni tehlikeli kişiyi kayıt eder."""
    registered_dangerous_faces[person_id] = embedding
    print(f"⚠️ YENİ tehlikeli kişi kaydedildi: {person_id}")


def clear_emotion_history():
    """Emotion geçmişini temizler."""
    emotion_history.clear()
