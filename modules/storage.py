"""modules.storage

Dosya kaydetme/yükleme ve yakalanan çıktıları yönetme işlemleri.

Bu proje iki tür kayıt tutar:
- dangerous_person: Tehlikeli kişi olarak kaydedilen ve embedding ile tekrar tanınabilen kayıtlar
- model_event: Model çıktısına göre alınan anlık kayıtlar (embedding'e eklenmez)
"""

import os
import json
import base64
import uuid
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np

from modules.config import CAPTURE_DIR
from modules.face_analysis import get_face_embedding, register_dangerous_person


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _safe_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "1", "yes", "y"}:
            return True
        if v in {"false", "0", "no", "n"}:
            return False
    return None


def _ensure_capture_dir() -> None:
    os.makedirs(CAPTURE_DIR, exist_ok=True)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_dangerous_person(
    person_id: str,
    timestamp: str,
    frame,
    emotions: Optional[Dict[str, Any]],
    meta: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    """Tehlikeli kişi kaydeder (görüntü + JSON).

    `meta` opsiyoneldir ve model çıktıları gibi ek alanlar içerir:
    - danger_score: float
    - is_thief: bool
    - thief_prob: float (0..1)
    - main_emotion: str
    - source/ip vb.
    """
    _ensure_capture_dir()

    img_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.jpg")
    cv2.imwrite(img_path, frame)

    meta = meta or {}
    data: Dict[str, Any] = {
        "type": "dangerous_person",
        "id": person_id,
        "timestamp": timestamp,
        "emotions": emotions,
        "main_emotion": meta.get("main_emotion"),
        "danger_score": _safe_float(meta.get("danger_score")),
        "is_thief": _safe_bool(meta.get("is_thief")),
        "thief_prob": _safe_float(meta.get("thief_prob")),
        "source": meta.get("source"),
        "ip": meta.get("ip"),
        "notes": meta.get("notes"),
    }

    json_path = os.path.join(CAPTURE_DIR, f"{person_id}_{timestamp}.json")
    _write_json(json_path, data)
    return img_path, json_path


def save_model_event(
    timestamp: str,
    frame,
    analysis: Optional[Dict[str, Any]] = None,
    event_id: Optional[str] = None,
) -> Tuple[str, str]:
    """Model çıktısına göre anlık kayıt alır (embedding'e eklenmez)."""
    _ensure_capture_dir()

    analysis = analysis or {}
    event_id = event_id or str(uuid.uuid4())[:8]
    base = f"event_{event_id}_{timestamp}"

    img_path = os.path.join(CAPTURE_DIR, f"{base}.jpg")
    cv2.imwrite(img_path, frame)

    data: Dict[str, Any] = {
        "type": "model_event",
        "id": event_id,
        "timestamp": timestamp,
        "emotions": analysis.get("emotions"),
        "main_emotion": analysis.get("main_emotion"),
        "danger_score": _safe_float(analysis.get("danger_score")),
        "is_thief": _safe_bool(analysis.get("is_thief")),
        "thief_prob": _safe_float(analysis.get("thief_prob")),
        "source": analysis.get("source"),
        "ip": analysis.get("ip"),
        "notes": analysis.get("notes"),
    }
    json_path = os.path.join(CAPTURE_DIR, f"{base}.json")
    _write_json(json_path, data)
    return img_path, json_path


def decode_base64_image(data_url_or_b64: str):
    """data:image/jpeg;base64,... veya düz base64 string'i OpenCV BGR frame'e çevirir."""
    if not data_url_or_b64:
        return None
    b64 = data_url_or_b64
    if "," in b64 and b64.strip().lower().startswith("data:"):
        b64 = b64.split(",", 1)[1]
    try:
        raw = base64.b64decode(b64)
        arr = np.frombuffer(raw, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def load_existing_faces():
    """Loads previously registered dangerous persons."""
    _ensure_capture_dir()
    for filename in os.listdir(CAPTURE_DIR):
        if filename.endswith(".json"):
            json_path = os.path.join(CAPTURE_DIR, filename)
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                record_type = data.get("type", "dangerous_person")
                if record_type != "dangerous_person":
                    continue

                person_id = data.get("id")
                if not person_id:
                    continue
                
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
    _ensure_capture_dir()
    files = os.listdir(CAPTURE_DIR)
    images = [f for f in files if f.endswith(".jpg")]
    return images
