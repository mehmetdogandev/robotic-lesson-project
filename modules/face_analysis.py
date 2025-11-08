import numpy as np
from deepface import DeepFace
from config import FACE_SIMILARITY_THRESHOLD
from storage import registered_dangerous_faces

def get_face_embedding(frame):
    try:
        embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=False)
        return np.array(embedding[0]["embedding"])
    except:
        return None

def is_registered_dangerous_person(current_embedding):
    if current_embedding is None:
        return False, None
    for person_id, saved_embedding in registered_dangerous_faces.items():
        similarity = np.dot(current_embedding, saved_embedding) / (
            np.linalg.norm(current_embedding) * np.linalg.norm(saved_embedding)
        )
        if similarity > FACE_SIMILARITY_THRESHOLD:
            return True, person_id  
    return False, None
