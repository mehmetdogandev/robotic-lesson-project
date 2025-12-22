

"""
Flask Web Application - Main file
Face recognition and emotion detection system
"""
from flask import Flask, render_template, Response, jsonify, request
import cv2
from modules.config import latest_state
from modules.camera import camera_stream
from modules.storage import get_captured_images
from modules import esp_client
from modules import face_analysis

app = Flask(__name__)

# Not: Tehlikeli kişi (embedding) kaydı kullanılmıyor.

# ESP32 OLED target URL - will be set by user
ESP32_OLED_URL = None




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
        from modules.config import (
            ANALYSIS_INTERVAL,
            DANGER_THRESHOLD,
            emotion_labels,
            latest_state,
            DANGER_COMPONENT_MIN_PERCENT,
            DANGER_COMPONENT_COUNT_MIN,
            DANGER_COMPONENT_MAX_MIN_PERCENT,
            DANGER_PERSISTENCE_SECONDS,
            DANGER_COOLDOWN_SECONDS,
            THIEF_PROB_THRESHOLD,
            ANGRY_ONLY_RISK_MIN_PERCENT,
            MODEL_RISK_GATING_ENABLED,
            MODEL_RISK_GATING_KEYS,
            MODEL_RISK_GATING_MIN_PERCENT,
        )
        from modules.face_analysis import (
            analyze_emotions, get_average_emotions, calculate_danger_score,
            get_face_embedding, is_registered_dangerous_person, register_dangerous_person,
            TemporalSmoother, emotions_dict_to_vector, vector_to_emotions_dict,
            predict_thief_risk
        )
        import uuid
        
        # MediaPipe Face Mesh (local instance for this generator)
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh_local = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        mp_drawing = mp.solutions.drawing_utils
        
        # Temporal smoother - iyileştirilmiş parametrelerle
        emotion_smoother = TemporalSmoother(maxlen=10, ema_alpha=0.7)
        last_danger_check = 0
        danger_candidate_since = None
        danger_active_until = 0.0
        
        url = f'http://{ip}:81/stream'

        def gen_from_ip_with_analysis():
            nonlocal last_danger_check, danger_candidate_since, danger_active_until
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

                    # 1) Duygu-tabanlı risk: önceki çoklu koşul + 'kızgın' çok yüksekse tek başına
                    angry_only_risk = angry >= float(ANGRY_ONLY_RISK_MIN_PERCENT)
                    emotion_risk = angry_only_risk or (
                        float(danger_score) >= float(DANGER_THRESHOLD)
                        and high_components >= int(DANGER_COMPONENT_COUNT_MIN)
                        and max_component >= float(DANGER_COMPONENT_MAX_MIN_PERCENT)
                    )

                    # 2) Model-tabanlı risk: thief_prob yüksekse ama sadece üzgün/korkmuş gibi durumlarda
                    # 'RISK' overlay'ini tetiklemesini engellemek için agresif duygu kapısı uygula.
                    model_risk_raw = float(thief_prob) >= float(THIEF_PROB_THRESHOLD)
                    if bool(MODEL_RISK_GATING_ENABLED):
                        aggressive_max = max(float(avg_emotions.get(k, 0.0)) for k in MODEL_RISK_GATING_KEYS)
                        model_risk = model_risk_raw and aggressive_max >= float(MODEL_RISK_GATING_MIN_PERCENT)
                    else:
                        model_risk = model_risk_raw

                    risk_condition = camera_stream.is_detection_enabled() and (emotion_risk or model_risk)

                    now = time.time()
                    if risk_condition:
                        if danger_candidate_since is None:
                            danger_candidate_since = now
                        if (now - danger_candidate_since) >= float(DANGER_PERSISTENCE_SECONDS):
                            danger_active_until = max(danger_active_until, now + float(DANGER_COOLDOWN_SECONDS))
                    else:
                        danger_candidate_since = None

                    danger = camera_stream.is_detection_enabled() and (now < danger_active_until)
                    
                    # Update latest state
                    latest_state["timestamp"] = time.strftime("%Y%m%d-%H%M%S")
                    latest_state["emotions"] = avg_emotions if avg_emotions else None
                    latest_state["main_emotion"] = main_emotion
                    latest_state["danger_score"] = float(danger_score)
                    latest_state["is_thief"] = is_thief
                    latest_state["thief_prob"] = thief_prob
                    latest_state["danger_active"] = bool(danger)
                    
                    # Send emotion to ESP32 OLED if URL is configured
                    if main_emotion and avg_emotions and face_analysis.ESP32_TARGET_URL:
                        confidence = avg_emotions.get(main_emotion, 0) / 100.0
                        face_analysis.send_emotion_to_esp32(main_emotion, confidence)
                    
                    # Draw emotion info on frame
                    y0 = 30
                    if avg_emotions and main_emotion:
                        emotion_text = f"Baskin Duygu: {emotion_labels.get(main_emotion, main_emotion)} ({avg_emotions.get(main_emotion, 0):.1f}%)"
                        cv2.putText(frame, emotion_text, (10, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        if is_thief:
                            cv2.putText(frame, f"THIEF DETECTED! ({thief_prob:.1%})", (10, y0 + 30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    
                    # Draw detection status
                    if not camera_stream.is_detection_enabled():
                        cv2.putText(frame, "ALGILAMA KAPALI", (10, y0 + 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128, 128, 128), 3)
                    
                    # Handle danger detection
                    if danger:
                        current_time = time.time()
                        if current_time - last_danger_check > 2:
                            face_embedding = get_face_embedding(rgb)
                            is_registered, existing_id = is_registered_dangerous_person(face_embedding)
                            
                            # Tehlikeli kişi kaydı DEVRE DIŞI: sadece UI tarafı /save_event ile model sonucuna göre kayıt alır.
                            if is_registered:
                                cv2.putText(frame, f"RISK DETECTED (KNOWN: {existing_id})", (10, y0 + 60),
                                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 140, 255), 3)
                            else:
                                cv2.putText(frame, "RISK TESPIT EDILDI", (10, y0 + 60),
                                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            last_danger_check = current_time
                    
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


@app.route('/save_event', methods=['POST'])
def save_event():
    """Save a model-driven snapshot + metadata from the frontend.

    JSON body:
      {
        "image": "data:image/jpeg;base64,..." | "<base64>",
        "timestamp": "YYYYmmdd-HHMMSS" (optional),
        "analysis": { ... } (optional)
      }
    """
    try:
        payload = request.get_json(silent=True) or {}
        image_b64 = payload.get('image')
        timestamp = (payload.get('timestamp') or '').strip()
        analysis = payload.get('analysis') or {}

        if not timestamp:
            import time
            timestamp = time.strftime("%Y%m%d-%H%M%S")

        from modules.storage import decode_base64_image, save_model_event
        frame = decode_base64_image(image_b64)
        if frame is None:
            return jsonify({"error": "Invalid image payload"}), 400

        img_path, json_path = save_model_event(timestamp, frame, analysis=analysis)
        return jsonify({"status": "ok", "image": img_path, "json": json_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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


@app.route('/esp_status', methods=['GET'])
def esp_status():
    """Get current ESP camera status and settings.
    
    Query param: ?ip=<esp_ip>
    """
    try:
        ip = request.args.get('ip')
        if not ip:
            ip = camera_stream.remote_ip
        if not ip:
            return jsonify({"error": "No ESP ip configured or provided"}), 400
        
        status, settings = esp_client.get_status(ip)
        if status == 200 and settings:
            return jsonify({"status": "success", "settings": settings}), 200
        else:
            return jsonify({"error": "Failed to get ESP status", "status_code": status}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/esp_apply_preset', methods=['POST'])
def esp_apply_preset():
    """Apply optimal camera settings preset for emotion analysis.
    
    JSON body: {"ip": "optional ip"}
    """
    try:
        payload = request.get_json(silent=True) or {}
        ip = payload.get('ip') or camera_stream.remote_ip
        if not ip:
            return jsonify({"error": "No ESP ip configured or provided"}), 400
        
        success = esp_client.apply_emotion_analysis_preset(ip)
        if success:
            return jsonify({"status": "success", "message": "Optimal settings applied"}), 200
        else:
            return jsonify({"error": "Some settings failed to apply"}), 500
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
        "is_thief": bool(latest_state.get("is_thief", False)),
        "thief_prob": float(latest_state.get("thief_prob", 0.0)),
    }
    return jsonify(data)


@app.route('/set_esp32_oled_url', methods=['POST'])
def set_esp32_oled_url():
    """Set ESP32 OLED display target URL for emotion transmission.
    
    JSON body: {"url": "http://10.64.220.189:2711/face_mood"}
    If url is empty or null, emotion transmission will be disabled.
    """
    try:
        payload = request.get_json(silent=True) or {}
        url = payload.get('url', '').strip()
        
        if url:
            # Validate URL format
            if not url.startswith('http://') and not url.startswith('https://'):
                return jsonify({"error": "URL must start with http:// or https://"}), 400
            
            if not '/face_mood' in url:
                return jsonify({"error": "URL must contain /face_mood endpoint"}), 400
            
            face_analysis.set_esp32_target_url(url)
            return jsonify({
                "status": "success",
                "message": "ESP32 OLED URL ayarlandı",
                "url": url
            }), 200
        else:
            face_analysis.set_esp32_target_url(None)
            return jsonify({
                "status": "success",
                "message": "ESP32 OLED iletimi devre dışı bırakıldı"
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_esp32_oled_url', methods=['GET'])
def get_esp32_oled_url():
    """Get current ESP32 OLED target URL."""
    return jsonify({
        "url": face_analysis.ESP32_TARGET_URL,
        "enabled": face_analysis.ESP32_TARGET_URL is not None
    })



# ============================================
# Application Startup
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Face Recognition and Emotion Detection System")
    print("=" * 60)
    print("✓ Modules loaded")
    print("✓ Registered persons loaded into memory")
    
    # Ask user for ESP32 OLED URL (optional)
    print("\n📟 ESP32 OLED Ekran Ayarları")
    print("-" * 60)
    esp_url = input("ESP32 OLED URL girin (opsiyonel, boş bırakabilirsiniz): ").strip()
    if esp_url:
        if not esp_url.startswith('http://') and not esp_url.startswith('https://'):
            esp_url = f"http://{esp_url}"
        if not '/face_mood' in esp_url:
            if not esp_url.endswith('/'):
                esp_url += '/'
            esp_url += 'face_mood'
        face_analysis.set_esp32_target_url(esp_url)
        print(f"✓ ESP32 OLED URL: {esp_url}")
    else:
        print("⚠️ ESP32 OLED iletimi devre dışı (URL girilmedi)")
    
    print("\n🌐 Starting application: http://0.0.0.0:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
