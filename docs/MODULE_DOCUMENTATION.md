# Module Documentation

This document describes each Python module in `modules/` and the important functions and classes they provide. Use this for developer onboarding and for extending the system.

---

## modules/config.py

Purpose: Central location for application-wide constants, configuration, and runtime shared state.

Public variables (names and meaning):
- `CAPTURE_DIR` (str): local path where captured images and metadata JSONs are stored (`static/captured`).
- `ANALYSIS_INTERVAL` (int): how many frames to skip between emotion analyses.
- `HISTORY_SIZE` (int): how many recent analyses are averaged for smoothing.
- `DANGER_THRESHOLD` (float): sum of angry+fear+disgust percentages above which a danger event is considered true.
- `FACE_SIMILARITY_THRESHOLD` (float): cosine-similarity threshold for considering a face as previously registered.
- `DETECTION_ENABLED` (bool): runtime toggle for enabling/disabling emotion detection flows.
- `emotion_labels` (dict): mapping DeepFace emotion keys to human-friendly labels (project uses Turkish labels but mapping is kept here).
- `latest_state` (dict): runtime store of the most recent timestamp, averaged emotions, dominant emotion and danger score.

Notes:
- This module is read by other modules. Changing constants here instantly affects behavior.

---

## modules/face_analysis.py

Purpose: Provide DeepFace-based operations: face embeddings, emotion analysis, history smoothing, and detection of previously-registered dangerous persons.

Key functions and behavior:

1. `get_face_embedding(frame) -> np.ndarray | None`
   - Input: `frame` — BGR or RGB image (as NumPy array) containing one or more faces.
   - Behavior: Calls `DeepFace.represent(..., model_name='Facenet', enforce_detection=False)` and returns the first embedding as a NumPy array. Returns `None` on failure.
   - Output: 1D NumPy array representing the face embedding.
   - Edge cases: If DeepFace cannot detect a face or model load fails, returns `None`.

2. `is_registered_dangerous_person(current_embedding) -> (bool, Optional[str])`
   - Input: `current_embedding` — NumPy array embedding for the current face.
   - Behavior: Compares `current_embedding` via cosine similarity to all embeddings stored in the in-memory `registered_dangerous_faces` dict. If similarity exceeds `FACE_SIMILARITY_THRESHOLD`, returns `(True, person_id)`.
   - Output: Tuple `(is_registered, person_id)`.
   - Edge cases: `current_embedding` is `None` → returns `(False, None)`.

3. `analyze_emotions(rgb_frame) -> dict | None`
   - Input: `rgb_frame` — RGB image expected by DeepFace.
   - Behavior: Calls `DeepFace.analyze(..., actions=['emotion'])`, extracts the `emotion` dict and appends it to a deque `emotion_history`. Returns the raw per-emotion dict on success, `None` on error while logging the exception.
   - Output: emotion probability dict (keys: 'angry','disgust','fear','happy','sad','surprise','neutral')

4. `get_average_emotions() -> (dict, str)`
   - Behavior: If `emotion_history` is empty, returns `({}, 'neutral')`. Otherwise computes the mean for each emotion across the deque and returns the averaged emotion dict and the `main_emotion` (key with highest mean).
   - Output: `(avg_emotions, main_emotion)`

5. `calculate_danger_score(avg_emotions) -> float`
   - Behavior: Returns `avg_emotions['angry'] + avg_emotions['fear'] + avg_emotions['disgust']` (handles missing keys safely).

6. `register_dangerous_person(person_id, embedding)`
   - Behavior: Stores `embedding` in `registered_dangerous_faces[person_id]` and logs a message.

7. `clear_emotion_history()`
   - Behavior: Clears the `emotion_history` deque.

Internal state:
- `emotion_history` (deque): ring buffer of last `HISTORY_SIZE` raw emotion dicts.
- `registered_dangerous_faces` (dict): in-memory map `{person_id: embedding}` used for recognition at runtime.

Persistence:
- Note that `registered_dangerous_faces` is populated at startup by reading files via `modules/storage.py`. The canonical persisted data is the JPG + JSON stored in `static/captured`.

---

## modules/storage.py

Purpose: Manage persistence of captured images and metadata and load previously captured faces at startup.

Key functions:

1. `save_dangerous_person(person_id, timestamp, frame, emotions) -> (img_path, json_path)`
   - Inputs:
     - `person_id` (str): unique identifier (e.g., 8-char UUID prefix)
     - `timestamp` (str): timestamp string used in file naming
     - `frame` (ndarray): BGR image to save as JPG
     - `emotions` (dict): averaged emotion dict saved into JSON
   - Behavior: Writes `{person_id}_{timestamp}.jpg` and `{person_id}_{timestamp}.json` into `CAPTURE_DIR`. Returns file paths.

2. `load_existing_faces()`
   - Behavior: On application start, iterates `CAPTURE_DIR` for `*.json` metadata files, reads the associated JPG image, obtains an embedding via `get_face_embedding()`, and if successful registers it in in-memory registry by calling `register_dangerous_person()`.
   - Notes: This allows the application to remember previously-detected dangerous people across restarts.

3. `get_captured_images() -> list[str]`
   - Behavior: Returns a list of filenames in `CAPTURE_DIR` that end with `.jpg`.

---

## modules/camera.py

Purpose: Interface with the webcam, perform frame-by-frame processing (mesh drawing, emotion analysis), and yield an MJPEG stream for Flask.

Key class: `CameraStream`

API and primary methods:

- `CameraStream.__init__()`
  - Initializes runtime flags such as `detection_enabled` and a `last_danger_check` timestamp used to rate-limit dangerous-person saves.

- `CameraStream.set_detection(enabled: bool)`
  - Toggles detection on/off at runtime.

- `CameraStream.is_detection_enabled() -> bool`
  - Returns current detection flag state.

- `CameraStream.draw_face_mesh(frame, rgb)`
  - Uses MediaPipe FaceMesh to draw landmark overlays onto `frame` (BGR) using the processed `rgb` array.

- `CameraStream.draw_emotion_info(frame, main_emotion, avg_emotions, y0=30)`
  - Renders the dominant emotion and its percentage on the frame.

- `CameraStream.draw_detection_status(frame, y0=30)`
  - If detection is disabled, draws a gray "DETECTION OFF" label.

- `CameraStream.handle_danger_detection(frame, rgb, avg_emotions, y0=30)`
  - Rate-limited (e.g., once per 5 seconds). Extracts an embedding, checks registry via `is_registered_dangerous_person()`. If new, creates a `person_id`, saves files via `save_dangerous_person()`, registers the embedding, and overlays a red alert on the frame. If the person was already registered, overlays a colored notification.

- `CameraStream.generate_frames()`
  - The main generator used by Flask's MJPEG response. Loop:
    1. Capture frame via OpenCV
    2. Flip and convert to RGB
    3. Draw face mesh
    4. Periodically call `analyze_emotions()` according to `ANALYSIS_INTERVAL`
    5. Compute `avg_emotions` and `main_emotion`
    6. Compute `danger_score` and decide whether to call `handle_danger_detection()`
    7. Update `latest_state` global dict with timestamp/emotions/dominant/danger_score
    8. Encode frame to JPEG and `yield` it as part of the MJPEG stream

Notes:
- The camera index is currently hard-coded to `0`. Change `cv2.VideoCapture(0)` to another index if needed.
- The class exposes a single module-level `camera_stream = CameraStream()` instance for `main.py` to use.

---

## main.py

Purpose: Flask application entry point. Sets up routes and starts the server.

Important routes and behavior:

- `GET /` — serves `templates/index.html`.
- `GET /video_feed` — returns a Response sourced from `camera_stream.generate_frames()` with MIME `multipart/x-mixed-replace; boundary=frame`.
- `GET /captured` — returns a JSON list of saved `.jpg` filenames in `CAPTURE_DIR` via `get_captured_images()`.
- `POST /set_detection` — accepts JSON `{"enabled": true|false}` to toggle detection. Returns the current state or a 400 error if payload invalid.
- `GET /status` — returns `{"enabled": <bool>}`.
- `GET /current_emotions` — returns the `latest_state` snapshot including `timestamp`, `emotions` (averaged), `main_emotion`, and `danger_score`.

Startup behavior:
- Calls `load_existing_faces()` at import-time (or on startup) to populate in-memory registered face embeddings.
- Prints a startup summary and runs Flask on `0.0.0.0:5000`.

---

## Extension points and how to modify behavior

- Change constants in `modules/config.py` to adjust detection sensitivity and temporal smoothing.
- Replace DeepFace model names if you prefer a different embedding model.
- Move persistence from filesystem to a DB by modifying `modules/storage.py` and updating `load_existing_faces()` to fetch embeddings from the DB.

---

End of module documentation.
