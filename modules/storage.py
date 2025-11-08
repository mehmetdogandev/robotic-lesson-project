import os, json, uuid
import cv2
import numpy as np
from face_analysis import get_face_embedding
from config import CAPTURE_DIR

os.makedirs(CAPTURE_DIR, exist_ok=True)

registered_dangerous_faces = {}

def load_existing_faces():
    for filename in os.listdir(CAPTURE_DIR):
        if filename.endswith(".json"):
            json_path = os.path.join(CAPTURE_DIR, filename)
            with open(json_path, "r") as f:
                data = json.load(f)
                person_id = data["id"]
                
                img_filename = filename.replace(".json", ".jpg")
                img_path = os.path.join(CAPTURE_DIR, img_filename)
                
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    embedding = get_face_embedding(img)
                    if embedding is not None:
                        registered_dangerous_faces[person_id] = embedding
                        print(f"✓ Kayıtlı tehlikeli kişi yüklendi: {person_id}")

def save_dangerous_person(frame, avg_emotions):
    person_id = str(uuid.uuid4())[:8]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    img_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.jpg")
    cv2.imwrite(img_path, frame)

    data = {
        "id": person_id,
        "timestamp": timestamp,
        "emotions": avg_emotions
    }
    json_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    return person_id
