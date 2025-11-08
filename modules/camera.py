import cv2, time
from collections import deque
from face_analysis import get_face_embedding, is_registered_dangerous_person
from storage import save_dangerous_person
from config import ANALYSIS_INTERVAL, DANGER_THRESHOLD, HISTORY_SIZE

emotion_history = deque(maxlen=HISTORY_SIZE)
DETECTION_ENABLED = True
latest_state = {"timestamp": None, "emotions": None, "main_emotion": None, "danger_score": 0.0}

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

        # Emotion analiz
        if DETECTION_ENABLED and frame_count % ANALYSIS_INTERVAL == 0:
            try:
                from deepface import DeepFace
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

        latest_state.update({
            "timestamp": time.strftime("%Y%m%d-%H%M%S"),
            "emotions": avg_emotions if avg_emotions else None,
            "main_emotion": main_emotion,
            "danger_score": float(danger_score),
        })

        # Tehlikeli kişi kontrolü
        if danger:
            current_time = time.time()
            if current_time - last_danger_check > 5:
                face_embedding = get_face_embedding(rgb)
                is_registered, existing_id = is_registered_dangerous_person(face_embedding)
                if not is_registered and face_embedding is not None:
                    person_id = save_dangerous_person(frame, avg_emotions)
                    print(f"⚠️ YENİ tehlikeli kişi kaydedildi: {person_id}")
                elif is_registered:
                    print(f"✓ Kayıtlı tehlikeli kişi tespit edildi: {existing_id}")
                last_danger_check = current_time

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        frame_count += 1
