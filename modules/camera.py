"""
Camera operations and video stream management
"""
import cv2
import time
import uuid
import mediapipe as mp
from modules.config import (
    ANALYSIS_INTERVAL, DANGER_THRESHOLD, emotion_labels, latest_state
)
from modules.face_analysis import (
    analyze_emotions, get_average_emotions, calculate_danger_score,
    get_face_embedding, is_registered_dangerous_person, register_dangerous_person
)
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
    
    def set_detection(self, enabled):
        """Sets detection status."""
        self.detection_enabled = enabled
    
    def is_detection_enabled(self):
        """Returns detection status."""
        return self.detection_enabled
    
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
    
    def handle_danger_detection(self, frame, rgb, avg_emotions, y0=30):
        """Handles dangerous situation detection."""
        current_time = time.time()
        
        # Check every 5 seconds
        if current_time - self.last_danger_check > 5:
            face_embedding = get_face_embedding(rgb)
            is_registered, existing_id = is_registered_dangerous_person(face_embedding)
            
            if not is_registered and face_embedding is not None:
                # New dangerous person - save
                person_id = str(uuid.uuid4())[:8]
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                
                save_dangerous_person(person_id, timestamp, frame, avg_emotions)
                register_dangerous_person(person_id, face_embedding)
                
                cv2.putText(frame, f"DANGEROUS PERSON! (NEW: {person_id})", (10, y0 + 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            
            elif is_registered:
                # Registered dangerous person
                print(f"✓ Registered dangerous person detected: {existing_id}")
                cv2.putText(frame, f"REGISTERED DANGEROUS PERSON: {existing_id}", (10, y0 + 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 140, 255), 3)
            else:
                # Face not recognized
                cv2.putText(frame, "DANGEROUS - Face not recognized", (10, y0 + 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            
            self.last_danger_check = current_time
        else:
            cv2.putText(frame, "DANGEROUS PERSON!", (10, y0 + 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    
    def generate_frames(self):
        """Generates frames for video stream."""
        cap = cv2.VideoCapture(0)
        frame_count = 0
        
        while True:
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
            
            # Calculate danger score
            danger_score = calculate_danger_score(avg_emotions)
            danger = self.detection_enabled and (danger_score > DANGER_THRESHOLD)
            
            # Update latest state
            latest_state["timestamp"] = time.strftime("%Y%m%d-%H%M%S")
            latest_state["emotions"] = avg_emotions if avg_emotions else None
            latest_state["main_emotion"] = main_emotion
            latest_state["danger_score"] = float(danger_score)
            
            # Draw information on frame
            y0 = 30
            self.draw_emotion_info(frame, main_emotion, avg_emotions, y0)
            self.draw_detection_status(frame, y0)
            
            # Check for dangerous situation
            if danger:
                self.handle_danger_detection(frame, rgb, avg_emotions, y0)
            
            # Encode frame and yield
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
        
        cap.release()


# Global camera instance
camera_stream = CameraStream()
