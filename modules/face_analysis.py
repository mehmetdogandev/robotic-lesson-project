"""
Face analysis, emotion detection, and person recognition operations
"""
import numpy as np
from deepface import DeepFace
from collections import deque
from modules.config import HISTORY_SIZE, FACE_SIMILARITY_THRESHOLD

# Emotion history
emotion_history = deque(maxlen=HISTORY_SIZE)

# Face embeddings of registered dangerous persons
registered_dangerous_faces = {}


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
        # Calculate cosine similarity
        similarity = np.dot(current_embedding, saved_embedding) / (
            np.linalg.norm(current_embedding) * np.linalg.norm(saved_embedding)
        )
        
        if similarity > FACE_SIMILARITY_THRESHOLD:
            return True, person_id  
    
    return False, None


def analyze_emotions(rgb_frame):
    """Performs emotion analysis from frame and adds to history."""
    try:
        analysis = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
        emotions = analysis[0]['emotion']
        emotion_history.append(emotions)
        return emotions
    except Exception as e:
        print("Analysis error:", e)
        return None


def get_average_emotions():
    """Calculates average from emotion history."""
    if not emotion_history:
        return {}, "neutral"
    
    avg_emotions = {k: np.mean([e[k] for e in emotion_history]) for k in emotion_history[0].keys()}
    main_emotion = max(avg_emotions, key=avg_emotions.get)
    
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
