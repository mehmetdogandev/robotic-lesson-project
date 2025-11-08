

from flask import Flask, render_template, Response, jsonify, request
import cv2
import os
import uuid
import json
import time
import numpy as np
from collections import deque
from deepface import DeepFace
import mediapipe as mp

app = Flask(__name__)

CAPTURE_DIR = "static/captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)




ANALYSIS_INTERVAL = 5     # her 5 karede bir analiz yap
HISTORY_SIZE = 3           # son 3 analizin ortalamasını al
DANGER_THRESHOLD = 70     # tehlike eşiği (angry+fear+disgust toplamı)
FACE_SIMILARITY_THRESHOLD = 0.6  # Yüz benzerlik eşiği (0-1 arası, düşük=daha sıkı)
emotion_history = deque(maxlen=HISTORY_SIZE)


registered_dangerous_faces = {} 


DETECTION_ENABLED = True
latest_state = {
    "timestamp": None,
    "emotions": None,
    "main_emotion": None,
    "danger_score": 0.0,
}


emotion_labels = {
    "happy": "Mutlu",
    "sad": "Uzgun",
    "angry": "Kizgin",
    "surprise": "Sasirmis",
    "fear": "Korkmus",
    "disgust": "Tiksinmi",
    "neutral": "Notr"
}


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
mp_drawing = mp.solutions.drawing_utils



def get_face_embedding(frame):
    """Bir frame'den yüz embedding'i (vektör) çıkarır."""
    try:
        embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=False)
        return np.array(embedding[0]["embedding"])
    except:
        return None

def is_registered_dangerous_person(current_embedding):
    """Mevcut yüzün daha önce kaydedilip kaydedilmediğini kontrol eder."""
    if current_embedding is None:
        return False, None
    
    for person_id, saved_embedding in registered_dangerous_faces.items():
        
        similarity = np.dot(current_embedding, saved_embedding) / (
            np.linalg.norm(current_embedding) * np.linalg.norm(saved_embedding)
        )
        
        if similarity > FACE_SIMILARITY_THRESHOLD:
            return True, person_id  
    
    return False, None  

def load_existing_faces():
    """Önceden kaydedilmiş tehlikeli kişileri yükler."""
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

load_existing_faces()


def generate_frames():
    cap = cv2.VideoCapture(0)
    frame_count = 0
    last_danger_check = 0  

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        
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

        
        if DETECTION_ENABLED and frame_count % ANALYSIS_INTERVAL == 0:
            try:
                analysis = DeepFace.analyze(rgb, actions=['emotion'], enforce_detection=False)
                emotions = analysis[0]['emotion']
                emotion_history.append(emotions)
            except Exception as e:
                print("Analiz hatası:", e)

        
        if emotion_history:
            avg_emotions = {k: np.mean([e[k] for e in emotion_history]) for k in emotion_history[0].keys()}
            main_emotion = max(avg_emotions, key=avg_emotions.get)
        else:
            avg_emotions = {}
            main_emotion = "neutral"

        
        danger_score = sum(avg_emotions.get(k, 0) for k in ["angry", "fear", "disgust"])
        danger = DETECTION_ENABLED and (danger_score > DANGER_THRESHOLD)

        
        latest_state["timestamp"] = time.strftime("%Y%m%d-%H%M%S")
        latest_state["emotions"] = avg_emotions if avg_emotions else None
        latest_state["main_emotion"] = main_emotion
        latest_state["danger_score"] = float(danger_score)

        
        y0 = 30
        cv2.putText(frame, f"Baskin Duygu: {emotion_labels.get(main_emotion, main_emotion)} ({avg_emotions.get(main_emotion, 0):.1f}%)",
                    (10, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        if not DETECTION_ENABLED:
            cv2.putText(frame, "ALGILAMA KAPALI", (10, y0 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128, 128, 128), 3)

        if danger:
            
            current_time = time.time()
            if current_time - last_danger_check > 5:
                
                face_embedding = get_face_embedding(rgb)
                is_registered, existing_id = is_registered_dangerous_person(face_embedding)
                
                if not is_registered and face_embedding is not None:
                    
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
                    
                    
                    registered_dangerous_faces[person_id] = face_embedding
                    
                    print(f"⚠️ YENİ tehlikeli kişi kaydedildi: {person_id}")
                    cv2.putText(frame, f"TEHLIKELI KISI! (YENİ: {person_id})", (10, y0 + 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    
                elif is_registered:
                    
                    print(f"✓ Kayıtlı tehlikeli kişi tespit edildi: {existing_id}")
                    cv2.putText(frame, f"KAYITLI TEHLIKELI KISI: {existing_id}", (10, y0 + 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 140, 255), 3)
                else:
                    
                    cv2.putText(frame, "TEHLIKELI - Yuz taninamadi", (10, y0 + 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                
                last_danger_check = current_time
            else:
                cv2.putText(frame, "TEHLIKELI KISI!", (10, y0 + 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

       
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        frame_count += 1




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/captured')
def get_captured():
    """Kaydedilen tehlikeli kişi dosyalarını listeler."""
    files = os.listdir(CAPTURE_DIR)
    images = [f for f in files if f.endswith(".jpg")]
    return jsonify(images)

@app.route('/set_detection', methods=['POST'])
def set_detection():
    """Algılama aç/kapat."""
    global DETECTION_ENABLED
    try:
        payload = request.get_json(silent=True) or {}
        enabled = payload.get('enabled')
        if isinstance(enabled, bool):
            DETECTION_ENABLED = enabled
            return jsonify({"enabled": DETECTION_ENABLED}), 200
        return jsonify({"error": "'enabled' (bool) bekleniyor"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    return jsonify({"enabled": DETECTION_ENABLED})

@app.route('/current_emotions')
def current_emotions():
    data = {
        "enabled": DETECTION_ENABLED,
        "timestamp": latest_state.get("timestamp"),
        "emotions": latest_state.get("emotions"),
        "main_emotion": latest_state.get("main_emotion"),
        "danger_score": latest_state.get("danger_score"),
    }
    return jsonify(data)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
