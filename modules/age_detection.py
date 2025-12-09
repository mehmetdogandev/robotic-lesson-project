"""
Age detection module using DeepFace
Modular age estimation without affecting existing emotion detection
"""
import numpy as np
from deepface import DeepFace
import cv2


def estimate_age(face_image):
    """
    Estimate age from a face image using DeepFace
    
    Args:
        face_image: RGB or BGR numpy array of face image
        
    Returns:
        int: Estimated age, or None if detection fails
    """
    try:
        # DeepFace expects RGB format
        if len(face_image.shape) == 3 and face_image.shape[2] == 3:
            # Check if BGR, convert to RGB
            if face_image.dtype == np.uint8:
                # Assume BGR from OpenCV, convert to RGB
                face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            else:
                face_rgb = face_image
        else:
            return None
            
        # Analyze age using DeepFace
        result = DeepFace.analyze(
            face_rgb,
            actions=['age'],
            enforce_detection=False,
            detector_backend='opencv',
            silent=True
        )
        
        # Handle both single face and multiple faces results
        if isinstance(result, list) and len(result) > 0:
            age = result[0].get('age', None)
        elif isinstance(result, dict):
            age = result.get('age', None)
        else:
            age = None
            
        return int(age) if age is not None else None
        
    except Exception as e:
        print(f"Age detection error: {e}")
        return None


def estimate_age_from_bbox(frame, bbox):
    """
    Estimate age from a face bounding box in frame
    
    Args:
        frame: Full frame image (BGR)
        bbox: Tuple of (x, y, w, h) for face region
        
    Returns:
        int: Estimated age, or None if detection fails
    """
    try:
        x, y, w, h = bbox
        
        # Add padding for better detection
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(frame.shape[1], x + w + padding)
        y2 = min(frame.shape[0], y + h + padding)
        
        # Crop face region
        face_crop = frame[y1:y2, x1:x2]
        
        if face_crop.size == 0:
            return None
            
        return estimate_age(face_crop)
        
    except Exception as e:
        print(f"Age estimation from bbox error: {e}")
        return None


def get_age_category(age):
    """
    Convert numeric age to category
    
    Args:
        age: Numeric age
        
    Returns:
        str: Age category (e.g., 'Çocuk', 'Genç', 'Yetişkin', 'Yaşlı')
    """
    if age is None:
        return "Bilinmiyor"
    
    if age < 13:
        return "Çocuk"
    elif age < 20:
        return "Genç"
    elif age < 40:
        return "Yetişkin"
    elif age < 60:
        return "Orta Yaşlı"
    else:
        return "Yaşlı"


class AgeEstimator:
    """
    Temporal age estimator with smoothing
    Reduces noise in age predictions
    """
    def __init__(self, history_size=5):
        self.history = []
        self.history_size = history_size
        
    def update(self, age):
        """Add new age estimate and return smoothed value"""
        if age is not None:
            self.history.append(age)
            if len(self.history) > self.history_size:
                self.history.pop(0)
        
        return self.get_smoothed_age()
    
    def get_smoothed_age(self):
        """Get median age from history (more robust than mean)"""
        if not self.history:
            return None
        
        # Use median for robustness against outliers
        return int(np.median(self.history))
    
    def reset(self):
        """Clear history"""
        self.history = []
