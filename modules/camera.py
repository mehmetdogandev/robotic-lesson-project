"""
Camera operations and video stream management
"""
import cv2
import numpy as np
from modules import esp_client
import time
import uuid
import mediapipe as mp
from modules.config import (
    ANALYSIS_INTERVAL, DANGER_THRESHOLD, emotion_labels, latest_state
)
from modules.config import (
    DANGER_COMPONENT_MIN_PERCENT,
    DANGER_COMPONENT_COUNT_MIN,
    DANGER_COMPONENT_MAX_MIN_PERCENT,
    DANGER_PERSISTENCE_SECONDS,
    DANGER_COOLDOWN_SECONDS,
    THIEF_PROB_THRESHOLD,
)
from modules.face_analysis import (
    analyze_emotions, get_average_emotions, calculate_danger_score,
    get_face_embedding, is_registered_dangerous_person, register_dangerous_person,
    predict_thief_risk
)
from modules.face_analysis import TemporalSmoother, emotions_dict_to_vector, vector_to_emotions_dict, preprocess_face
from modules.storage import save_dangerous_person

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
mp_drawing = mp.solutions.drawing_utils


class CameraStream:
    """Camera stream management and frame processing"""
    
    def __init__(self):
        self.detection_enabled = True
        self.last_danger_check = 0
        # If remote_ip is set, frames will be pulled from ESP via HTTP
        self.remote_ip = None
        # small backoff between remote fetches to avoid overloading ESP
        self._remote_delay = 0.1
        # temporal smoother - iyileştirilmiş parametrelerle
        self.emotion_smoother = TemporalSmoother(maxlen=10, ema_alpha=0.7)

        # Risk gating (false-positive azaltma)
        self._danger_candidate_since = None
        self._danger_active_until = 0.0
    
    def set_detection(self, enabled):
        """Sets detection status."""
        self.detection_enabled = enabled
    
    def is_detection_enabled(self):
        """Returns detection status."""
        return self.detection_enabled

    def set_remote_ip(self, ip: str):
        """Set an ESP IP to use as frame source. Pass None to clear."""
        if ip:
            self.remote_ip = ip
        else:
            self.remote_ip = None

    def clear_remote_ip(self):
        self.remote_ip = None

    def is_using_remote(self):
        return bool(self.remote_ip)
    
    def draw_face_mesh(self, frame, rgb):
        """Draws face mesh on frame."""
        results = face_mesh.process(rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )
    
    def draw_emotion_info(self, frame, main_emotion, avg_emotions, y0=30):
        """Draws emotion information on frame."""
        emotion_text = f"Baskin Duygu: {emotion_labels.get(main_emotion, main_emotion)} ({avg_emotions.get(main_emotion, 0):.1f}%)"
        cv2.putText(frame, emotion_text, (10, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    def draw_detection_status(self, frame, y0=30):
        """Draws warning if detection is off."""
        if not self.detection_enabled:
            cv2.putText(frame, "ALGILAMA KAPALI", (10, y0 + 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128, 128, 128), 3)
    
    def handle_danger_detection(self, frame, rgb, avg_emotions, analysis_meta=None, y0=30):
        """Handles dangerous situation detection."""
        current_time = time.time()
        analysis_meta = analysis_meta or {}
        
        # Tehlikeli kişi kaydı DEVRE DIŞI: sadece UI tarafı /save_event ile model sonucuna göre kayıt alır.
        # Bu fonksiyon artık sadece overlay basar (spam engeli için aralıklı).
        if current_time - self.last_danger_check > 2:
            cv2.putText(frame, "RISK TESPIT EDILDI", (10, y0 + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            self.last_danger_check = current_time
    
    def generate_frames(self):
        """Generates frames for video stream.

        If `self.remote_ip` is set, fetch single JPEG snapshots from the ESP
        and use them as the frame source. Otherwise fall back to local camera
        capture (index 0) and the existing analysis pipeline.
        """
        frame_count = 0

        # Local capture object (created lazily only if needed)
        cap = None

        while True:
            if self.remote_ip:
                # Fetch JPEG bytes from ESP
                jpeg = esp_client.get_snapshot(self.remote_ip)
                if not jpeg:
                    # yield a short error frame or retry
                    # (we simply sleep briefly and continue)
                    time.sleep(self._remote_delay)
                    continue
                # decode JPEG bytes into OpenCV image
                arr = np.frombuffer(jpeg, dtype=np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame is None:
                    time.sleep(self._remote_delay)
                    continue
                # No horizontal flip for remote stream by default
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                if cap is None:
                    cap = cv2.VideoCapture(0)
                success, frame = cap.read()
                if not success:
                    break
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Draw face mesh
            self.draw_face_mesh(frame, rgb)
            
            # Perform emotion analysis (at intervals)
            if self.detection_enabled and frame_count % ANALYSIS_INTERVAL == 0:
                analyze_emotions(rgb)
            
            # Calculate average emotions
            avg_emotions, main_emotion = get_average_emotions()

            # Apply temporal smoothing to the averaged emotions for stability
            if avg_emotions:
                vec = emotions_dict_to_vector(avg_emotions)
                smoothed = self.emotion_smoother.update(vec)
                if smoothed is not None:
                    avg_emotions = vector_to_emotions_dict(smoothed)
                    main_emotion = max(avg_emotions, key=avg_emotions.get)
            
            # Calculate danger score
            danger_score = calculate_danger_score(avg_emotions)
            
            # Predict Thief Risk
            is_thief, thief_prob = False, 0.0
            if avg_emotions:
                is_thief, thief_prob = predict_thief_risk(avg_emotions)

            # Daha gerçekçi risk kararı: çoklu koşul + süreklilik + cooldown
            angry = float(avg_emotions.get("angry", 0.0))
            fear = float(avg_emotions.get("fear", 0.0))
            disgust = float(avg_emotions.get("disgust", 0.0))
            components = [angry, fear, disgust]
            high_components = sum(1 for v in components if v >= float(DANGER_COMPONENT_MIN_PERCENT))
            max_component = max(components) if components else 0.0
            emotion_risk = (
                float(danger_score) >= float(DANGER_THRESHOLD)
                and high_components >= int(DANGER_COMPONENT_COUNT_MIN)
                and max_component >= float(DANGER_COMPONENT_MAX_MIN_PERCENT)
            )
            model_risk = float(thief_prob) >= float(THIEF_PROB_THRESHOLD)
            risk_condition = self.detection_enabled and (emotion_risk or model_risk)

            now = time.time()
            if risk_condition:
                if self._danger_candidate_since is None:
                    self._danger_candidate_since = now
                if (now - self._danger_candidate_since) >= float(DANGER_PERSISTENCE_SECONDS):
                    self._danger_active_until = max(self._danger_active_until, now + float(DANGER_COOLDOWN_SECONDS))
            else:
                self._danger_candidate_since = None

            danger = self.detection_enabled and (now < self._danger_active_until)
            
            # Update latest state
            latest_state["timestamp"] = time.strftime("%Y%m%d-%H%M%S")
            latest_state["emotions"] = avg_emotions if avg_emotions else None
            latest_state["main_emotion"] = main_emotion
            latest_state["danger_score"] = float(danger_score)
            latest_state["is_thief"] = is_thief
            latest_state["thief_prob"] = thief_prob
            latest_state["danger_active"] = bool(danger)
            
            # Send emotion to ESP32 OLED if URL is configured
            from modules.face_analysis import send_emotion_to_esp32, ESP32_TARGET_URL
            if main_emotion and avg_emotions and ESP32_TARGET_URL:
                confidence = avg_emotions.get(main_emotion, 0) / 100.0
                send_emotion_to_esp32(main_emotion, confidence)
            
            # Draw information on frame
            y0 = 30
            self.draw_emotion_info(frame, main_emotion, avg_emotions, y0)
            
            if is_thief:
                cv2.putText(frame, f"THIEF DETECTED! ({thief_prob:.1%})", (10, y0 + 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

            self.draw_detection_status(frame, y0)
            
            # Check for dangerous situation
            if danger:
                analysis_meta = {
                    "main_emotion": main_emotion,
                    "danger_score": float(danger_score),
                    "is_thief": bool(is_thief),
                    "thief_prob": float(thief_prob),
                    "source": "esp" if self.remote_ip else "local",
                    "ip": self.remote_ip,
                }
                self.handle_danger_detection(frame, rgb, avg_emotions, analysis_meta, y0)
            
            # Encode frame and yield
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
        
        if cap is not None:
            cap.release()


# Global camera instance
camera_stream = CameraStream()
