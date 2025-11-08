"""
File saving, loading, and management operations
"""
import os
import json
import cv2
from modules.config import CAPTURE_DIR
from modules.face_analysis import get_face_embedding, register_dangerous_person


def save_dangerous_person(person_id, timestamp, frame, emotions):
    """Saves the image and information of a dangerous person."""
    # Save image
    img_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.jpg")
    cv2.imwrite(img_path, frame)
    
    # Save data as JSON
    data = {
        "id": person_id,
        "timestamp": timestamp,
        "emotions": emotions
    }
    json_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)
    
    return img_path, json_path


def load_existing_faces():
    """Loads previously registered dangerous persons."""
    for filename in os.listdir(CAPTURE_DIR):
        if filename.endswith(".json"):
            json_path = os.path.join(CAPTURE_DIR, filename)
            with open(json_path, "r") as f:
                data = json.load(f)
                person_id = data["id"]
                
                # Find the related image
                img_filename = filename.replace(".json", ".jpg")
                img_path = os.path.join(CAPTURE_DIR, img_filename)
                
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    embedding = get_face_embedding(img)
                    if embedding is not None:
                        register_dangerous_person(person_id, embedding)
                        print(f"✓ Registered dangerous person loaded: {person_id}")


def get_captured_images():
    """Lists captured images of dangerous persons."""
    files = os.listdir(CAPTURE_DIR)
    images = [f for f in files if f.endswith(".jpg")]
    return images
