"""
Dosya kaydetme, yükleme ve yönetim işlemleri
"""
import os
import json
import cv2
from modules.config import CAPTURE_DIR
from modules.face_analysis import get_face_embedding, register_dangerous_person


def save_dangerous_person(person_id, timestamp, frame, emotions):
    """Tehlikeli kişinin görüntüsünü ve bilgilerini kaydeder."""
    # Görüntüyü kaydet
    img_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.jpg")
    cv2.imwrite(img_path, frame)
    
    # Verileri JSON olarak kaydet
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
    """Önceden kaydedilmiş tehlikeli kişileri yükler."""
    for filename in os.listdir(CAPTURE_DIR):
        if filename.endswith(".json"):
            json_path = os.path.join(CAPTURE_DIR, filename)
            with open(json_path, "r") as f:
                data = json.load(f)
                person_id = data["id"]
                
                # İlgili görüntüyü bul
                img_filename = filename.replace(".json", ".jpg")
                img_path = os.path.join(CAPTURE_DIR, img_filename)
                
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    embedding = get_face_embedding(img)
                    if embedding is not None:
                        register_dangerous_person(person_id, embedding)
                        print(f"✓ Kayıtlı tehlikeli kişi yüklendi: {person_id}")


def get_captured_images():
    """Kaydedilen tehlikeli kişi görüntülerini listeler."""
    files = os.listdir(CAPTURE_DIR)
    images = [f for f in files if f.endswith(".jpg")]
    return images
