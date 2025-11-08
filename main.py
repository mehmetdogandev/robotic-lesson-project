

"""
Flask Web Application - Main file
Face recognition and emotion detection system
"""
from flask import Flask, render_template, Response, jsonify, request
import cv2
from modules.config import latest_state
from modules.camera import camera_stream
from modules.storage import load_existing_faces, get_captured_images
from modules import esp_client

app = Flask(__name__)

# Load registered persons on application startup
load_existing_faces()




# ============================================
# Flask Routes
# ============================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video stream endpoint"""
    # Optional query parameter `ip` allows the frontend to request the
    # stream from an ESP32 / IP camera (e.g. http://<ip>:81/stream).
    ip = request.args.get('ip')
    if ip:
        # Import necessary modules for processing
        import time
        import numpy as np
        import mediapipe as mp
        from modules.config import ANALYSIS_INTERVAL, DANGER_THRESHOLD, emotion_labels, latest_state
        from modules.face_analysis import (
            analyze_emotions, get_average_emotions, calculate_danger_score,
            get_face_embedding, is_registered_dangerous_person, register_dangerous_person,
            TemporalSmoother, emotions_dict_to_vector, vector_to_emotions_dict
        )
        from modules.storage import save_dangerous_person
        import uuid
        
        # MediaPipe Face Mesh (local instance for this generator)
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh_local = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        mp_drawing = mp.solutions.drawing_utils
        
        # Temporal smoother for remote stream
        emotion_smoother = TemporalSmoother(maxlen=8, ema_alpha=0.6)
        last_danger_check = 0
        
        url = f'http://{ip}:81/stream'

        def gen_from_ip_with_analysis():
            nonlocal last_danger_check
            cap = cv2.VideoCapture(url)
            frame_count = 0
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Convert to RGB for analysis
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Draw face mesh
                    results = face_mesh_local.process(rgb)
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            mp_drawing.draw_landmarks(
                                image=frame,
                                landmark_list=face_landmarks,
                                connections=mp_face_mesh.FACEMESH_TESSELATION,
                                landmark_drawing_spec=None,
                                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                            )
                    
                    # Perform emotion analysis at intervals
                    if camera_stream.is_detection_enabled() and frame_count % ANALYSIS_INTERVAL == 0:
                        analyze_emotions(rgb)
                    
                    # Get average emotions
                    avg_emotions, main_emotion = get_average_emotions()
                    
                    # Apply temporal smoothing
                    if avg_emotions:
                        vec = emotions_dict_to_vector(avg_emotions)
                        smoothed = emotion_smoother.update(vec)
                        if smoothed is not None:
                            avg_emotions = vector_to_emotions_dict(smoothed)
                            main_emotion = max(avg_emotions, key=avg_emotions.get)
                    
                    # Calculate danger score
                    danger_score = calculate_danger_score(avg_emotions)
                    danger = camera_stream.is_detection_enabled() and (danger_score > DANGER_THRESHOLD)
                    
                    # Update latest state
                    latest_state["timestamp"] = time.strftime("%Y%m%d-%H%M%S")
                    latest_state["emotions"] = avg_emotions if avg_emotions else None
                    latest_state["main_emotion"] = main_emotion
                    latest_state["danger_score"] = float(danger_score)
                    
                    # Draw emotion info on frame
                    y0 = 30
                    if avg_emotions and main_emotion:
                        emotion_text = f"Baskin Duygu: {emotion_labels.get(main_emotion, main_emotion)} ({avg_emotions.get(main_emotion, 0):.1f}%)"
                        cv2.putText(frame, emotion_text, (10, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    # Draw detection status
                    if not camera_stream.is_detection_enabled():
                        cv2.putText(frame, "ALGILAMA KAPALI", (10, y0 + 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128, 128, 128), 3)
                    
                    # Handle danger detection
                    if danger:
                        current_time = time.time()
                        if current_time - last_danger_check > 5:
                            face_embedding = get_face_embedding(rgb)
                            is_registered, existing_id = is_registered_dangerous_person(face_embedding)
                            
                            if not is_registered and face_embedding is not None:
                                person_id = str(uuid.uuid4())[:8]
                                timestamp = time.strftime("%Y%m%d-%H%M%S")
                                save_dangerous_person(person_id, timestamp, frame, avg_emotions)
                                register_dangerous_person(person_id, face_embedding)
                                cv2.putText(frame, f"DANGEROUS PERSON! (NEW: {person_id})", (10, y0 + 60), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            elif is_registered:
                                print(f"✓ Registered dangerous person detected: {existing_id}")
                                cv2.putText(frame, f"REGISTERED DANGEROUS PERSON: {existing_id}", (10, y0 + 60), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 140, 255), 3)
                            else:
                                cv2.putText(frame, "DANGEROUS - Face not recognized", (10, y0 + 60), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            last_danger_check = current_time
                        else:
                            cv2.putText(frame, "DANGEROUS PERSON!", (10, y0 + 60), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    
                    # Encode and yield frame
                    ret2, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                    frame_count += 1
                    
            finally:
                cap.release()

        return Response(gen_from_ip_with_analysis(), mimetype='multipart/x-mixed-replace; boundary=frame')

    # Fall back to the local / default camera stream with analysis
    return Response(camera_stream.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/captured')
def get_captured():
    """Lists captured dangerous person files."""
    images = get_captured_images()
    return jsonify(images)


@app.route('/set_camera_source', methods=['POST'])
def set_camera_source():
    """Switch camera source between 'local' and 'esp'.

    JSON body: {"mode": "esp"|"local", "ip": "10.0.0.12"}
    """
    try:
        payload = request.get_json(silent=True) or {}
        mode = payload.get('mode')
        ip = payload.get('ip')

        if mode == 'esp':
            if not ip:
                return jsonify({"error": "ip required for mode 'esp'"}), 400
            camera_stream.set_remote_ip(ip)
            return jsonify({"mode": "esp", "ip": ip}), 200
        elif mode == 'local':
            camera_stream.clear_remote_ip()
            return jsonify({"mode": "local"}), 200
        else:
            return jsonify({"error": "mode must be 'esp' or 'local'"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/esp_command', methods=['POST'])
def esp_command():
    """Forward a command to the configured ESP device (or ip in payload).

    JSON body: {"params": { ... }, "ip": "optional ip"}
    Returns the HTTP status and JSON/text response from the ESP.
    """
    try:
        payload = request.get_json(silent=True) or {}
        params = payload.get('params') or {}
        ip = payload.get('ip') or camera_stream.remote_ip
        if not ip:
            return jsonify({"error": "No ESP ip configured or provided"}), 400
        status, body = esp_client.send_command(ip, params)
        return jsonify({"status": status, "body": body}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/set_detection', methods=['POST'])
def set_detection():
    """Toggle detection on/off."""
    try:
        payload = request.get_json(silent=True) or {}
        enabled = payload.get('enabled')
        
        if isinstance(enabled, bool):
            camera_stream.set_detection(enabled)
            return jsonify({"enabled": camera_stream.is_detection_enabled()}), 200
        
        return jsonify({"error": "'enabled' (bool) expected"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/status')
def status():
    """Returns detection status."""
    return jsonify({"enabled": camera_stream.is_detection_enabled()})


@app.route('/current_emotions')
def current_emotions():
    """Returns current emotion data."""
    data = {
        "enabled": camera_stream.is_detection_enabled(),
        "timestamp": latest_state.get("timestamp"),
        "emotions": latest_state.get("emotions"),
        "main_emotion": latest_state.get("main_emotion"),
        "danger_score": latest_state.get("danger_score"),
    }
    return jsonify(data)



# ============================================
# Application Startup
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Face Recognition and Emotion Detection System")
    print("=" * 60)
    print("✓ Modules loaded")
    print("✓ Registered persons loaded into memory")
    print("🌐 Starting application: http://0.0.0.0:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
