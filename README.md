#  Robotic Face Recognition and Emotion Analysis System

![Python Version](https://img.shields.io/badge/Python-3.10.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-0.0.93-orange.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.21-red.svg)

**Real-time face recognition, emotion analysis, and dangerous person detection system**

---

##  Features

###  Core Features
-  **Real-Time Face Detection**: High-performance face mesh visualization with MediaPipe
-  **Emotion Analysis**: 7 different emotion detection using DeepFace library (Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral)
-  **Dangerous Person Detection**: Automatic alert system for negative emotions
-  **Face Recognition & Registration**: Person identification using FaceNet embeddings and database management
-  **Web Interface**: User-friendly Flask-based web interface
-  **REST API**: Comprehensive API endpoints for external system integration

###  Technical Features
-  **AI Models**: DeepFace (VGG-Face, FaceNet) + MediaPipe Face Mesh
-  **Emotion History**: More stable results with averaging of last N analyses
-  **Cosine Similarity**: Mathematical approach for face similarity
-  **Auto Save**: Automatic saving of images and metadata for dangerous persons
-  **Dynamic Detection**: Detection mode that can be toggled on/off at runtime

---

##  Project Structure

```
robotik/
  main.py                    # Flask application and HTTP routes
  requirements.txt           # Python dependencies
  README.md                  # Project documentation

  modules/                   #  Modular code structure
    __init__.py              # Module package definition
    config.py                #  Configuration constants
    face_analysis.py         #  Face analysis and emotion detection
    storage.py               #  File saving and loading operations
    camera.py                #  Camera stream and video frame processing

  static/
     captured/             #  Dangerous person images (auto-created)
        {person_id}_{timestamp}.jpg
        {person_id}_{timestamp}.json

  templates/
     index.html               #  Web interface HTML template
```

---

##  Module Structure

### 1 `config.py` - Configuration
Central management of all system parameters:

```python
ANALYSIS_INTERVAL = 5        # Analyze every N frames
HISTORY_SIZE = 3             # Number of analyses to average
DANGER_THRESHOLD = 70        # Danger score threshold (angry+fear+disgust)
FACE_SIMILARITY_THRESHOLD = 0.6  # Face similarity threshold (0-1 range)
```

**Contents:**
- Directory configuration
- Analysis parameters
- Emotion labels (Turkish mapping)
- Global state management

---

### 2 `face_analysis.py` - Face Analysis
AI-based face recognition and emotion analysis:

**Functions:**
- `get_face_embedding()` - Extract 128-dimensional embedding with FaceNet
- `is_registered_dangerous_person()` - Person recognition using cosine similarity
- `analyze_emotions()` - Detect 7 emotions with DeepFace
- `get_average_emotions()` - Calculate average for temporal smoothing
- `calculate_danger_score()` - Danger scoring
- `register_dangerous_person()` - Register new person

**Technologies Used:**
- DeepFace (VGG-Face, FaceNet)
- NumPy (vector operations)
- Collections.deque (ring buffer)

---

### 3 `storage.py` - Data Management
File system and persistence operations:

**Functions:**
- `save_dangerous_person()` - Save person data as JPG + JSON
- `load_existing_faces()` - Load registered persons on startup
- `get_captured_images()` - List captured images

**Data Format:**
```json
{
  "id": "a3f7c2d1",
  "timestamp": "20251108-143052",
  "emotions": {
    "angry": 78.5,
    "disgust": 12.3,
    "fear": 5.2,
    ...
  }
}
```

---

### 4 `camera.py` - Video Stream
Camera management and real-time processing:

**CameraStream Class:**
- `generate_frames()` - Video stream generator (MJPEG)
- `draw_face_mesh()` - MediaPipe face mesh overlay
- `draw_emotion_info()` - Draw emotion info on frame
- `handle_danger_detection()` - Handle dangerous situation

**Processing Pipeline:**
1. Read camera frame
2. Draw face mesh (MediaPipe)
3. Perform emotion analysis (every 5 frames)
4. Calculate average emotions
5. Evaluate danger score
6. Save person if necessary
7. Encode frame and stream

---

### 5 `main.py` - Flask Application
HTTP server and API endpoints:

**Routes:**
- `GET /` - Home page
- `GET /video_feed` - MJPEG video stream
- `GET /captured` - List of registered persons
- `POST /set_detection` - Toggle detection on/off
- `GET /status` - System status
- `GET /current_emotions` - Real-time emotion data

---

##  Installation

###  Requirements

- **Python 3.10.11** (Recommended - for TensorFlow compatibility)
- **Webcam** (for video stream)
- **4GB+ RAM** (for AI models)
- **Internet connection** (for downloading models on first run)

---

###  Step 1: Python Installation

#### Windows:
```powershell
# Download Python 3.10.11
# https://www.python.org/downloads/release/python-31011/

# Run the downloaded .exe file
#  Make sure to check "Add Python to PATH"!

# Verify installation
python --version
# Output: Python 3.10.11
```

#### Linux/Mac:
```bash
# Install Python 3.10.11 using pyenv (recommended)
pyenv install 3.10.11
pyenv local 3.10.11

# Or use system package manager
sudo apt install python3.10  # Ubuntu/Debian
brew install python@3.10     # macOS
```

---

###  Step 2: Create Virtual Environment

A virtual environment isolates your project dependencies from system Python.

```bash
# Navigate to project directory
cd c:\Users\ANDCARBPROJE2\Desktop\robotik

# Create virtual environment
python -m venv .venv
```

**The `.venv` folder will be created** - This stores Python and all libraries.

---

###  Step 3: Activate Virtual Environment

#### Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1

# If you get "execution policy" error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try again
```

#### Windows CMD:
```cmd
.venv\Scripts\activate.bat
```

#### Linux/Mac:
```bash
source .venv/bin/activate
```

** Successful activation**: You'll see `(.venv)` at the start of your terminal prompt:
```
(.venv) PS C:\Users\ANDCARBPROJE2\Desktop\robotik>
```

---

###  Step 4: Install Dependencies

```bash
# Install all required libraries
pip install -r requirements.txt

# This may take 5-10 minutes (large packages like TensorFlow, PyTorch, etc.)
```

**Main Libraries to be Installed:**
- `Flask` (Web framework)
- `deepface` (AI face analysis)
- `mediapipe` (Face mesh)
- `opencv-python` (Image processing)
- `tensorflow` (Deep learning backend)
- `torch` (For FaceNet)

---

###  Step 5: Verify Installation

```bash
# Check Python version
python --version
# Output: Python 3.10.11

# Check required packages
pip list | Select-String -Pattern "deepface|mediapipe|flask"
# Should see: deepface, mediapipe, Flask packages
```

---

##  Usage

###  Start the Application

```bash
# Make sure virtual environment is active (you see .venv)
python main.py
```

**Expected Output:**
```
============================================================
 Face Recognition and Emotion Detection System
============================================================
 Modules loaded
 Registered persons loaded into memory
 Starting application: http://0.0.0.0:5000
============================================================
 * Serving Flask app 'main'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
```

---

###  Access Web Interface

Open these addresses in your browser:

- **Local:** http://localhost:5000
- **Network:** http://192.168.x.x:5000 (for other devices on same network)

---

###  User Interface

1. **Video Stream**: Real-time camera feed
2. **Face Mesh**: Green landmark points on face
3. **Emotion Display**: "Dominant Emotion" shown at top of screen
4. **Danger Alert**: Red warning when dangerous situation detected

**Keyboard Controls** (can be added to web interface):
- `Space` - Pause/resume detection
- `R` - Reset emotion history
- `Esc` - Exit

---

##  API Documentation

### 1. Video Stream
```http
GET /video_feed
```
**Response:** MJPEG stream  
**Usage:** `<img src="/video_feed">`

---

### 2. List Registered Persons
```http
GET /captured
```
**Response:**
```json
[
  "a3f7c2d1_20251108-143052.jpg",
  "b8e9d4f2_20251108-144123.jpg"
]
```

---

### 3. Control Detection
```http
POST /set_detection
Content-Type: application/json

{
  "enabled": true
}
```
**Response:**
```json
{
  "enabled": true
}
```

---

### 4. System Status
```http
GET /status
```
**Response:**
```json
{
  "enabled": true
}
```

---

### 5. Current Emotions
```http
GET /current_emotions
```
**Response:**
```json
{
  "enabled": true,
  "timestamp": "20251108-143052",
  "emotions": {
    "angry": 15.2,
    "disgust": 2.1,
    "fear": 5.8,
    "happy": 45.3,
    "sad": 12.4,
    "surprise": 8.7,
    "neutral": 10.5
  },
  "main_emotion": "happy",
  "danger_score": 23.1
}
```

---

##  Configuration

Customize system behavior by editing `modules/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ANALYSIS_INTERVAL` | 5 | How many frames between analyses (lower = more frequent) |
| `HISTORY_SIZE` | 3 | Number of analyses to average (higher = smoother) |
| `DANGER_THRESHOLD` | 70 | Danger score threshold (angry+fear+disgust sum) |
| `FACE_SIMILARITY_THRESHOLD` | 0.6 | Face recognition sensitivity (0.5=strict, 0.8=loose) |

**Example Customization:**
```python
# For more sensitive danger detection
DANGER_THRESHOLD = 50  # Lower threshold

# For smoother emotion transitions
HISTORY_SIZE = 5  # More sample averaging

# For more frequent analysis
ANALYSIS_INTERVAL = 3  # Every 3 frames
```

---

##  Troubleshooting

###  "No module named 'tensorflow'" Error
```bash
# Manually install TensorFlow
pip install tensorflow==2.12.0
```

###  Camera won't open
```python
# Change camera index in camera.py
cap = cv2.VideoCapture(0)  # Try 1, 2, ... instead of 0
```

###  "ImportError: DLL load failed"
```bash
# Install Visual C++ Redistributable (Windows)
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

###  Model download error
```bash
# Check your internet connection
# ~200MB models downloaded on first run

# Manual model download:
python -c "from deepface import DeepFace; DeepFace.build_model('VGG-Face')"
```

###  Port already in use
```python
# Change port in main.py
app.run(host='0.0.0.0', port=5001)  # Use 5001 instead of 5000
```

---

##  Performance Tips

1. **GPU Support**: If CUDA is installed, TensorFlow will automatically use GPU
2. **Frame Rate**: Increase `ANALYSIS_INTERVAL` to boost FPS
3. **Memory**: Registering many persons increases RAM usage
4. **Resolution**: Lower camera resolution to speed up processing

---

##  Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10.11 | Main programming language |
| Flask | 3.1.2 | Web framework |
| DeepFace | 0.0.93 | Face analysis and emotion detection |
| MediaPipe | 0.10.21 | Face mesh rendering |
| OpenCV | 4.10.0 | Image processing |
| TensorFlow | 2.12.0 | Deep learning backend |
| PyTorch | 2.2.2 | FaceNet model |
| NumPy | 1.26.4 | Vector operations |

---

##  Important Notes

###  Security
- Camera access required (browser permission)
- Registered faces stored locally (GDPR compliant)
- Use HTTPS in production

###  Data Storage
- Per dangerous person: 1 JPG + 1 JSON file
- Average size: ~50KB per person
- Location: `static/captured/`

###  Model Performance
- Model download on first run: ~200MB
- Analysis time: ~100-200ms per frame (CPU)
- With GPU: ~20-50ms per frame

###  Updates
- Regularly run `pip install --upgrade deepface`
- Keep requirements.txt up to date
- Stay on Python 3.10.x series (TensorFlow compatibility)

---

##  Contributing

To improve the project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

##  Contact

**Project Owner:** Mehmet Doğan  
**Repository:** [robotic-lesson-project](https://github.com/mehmetdogandev/robotic-lesson-project)

---

##  License

This project is for educational purposes. Check relevant AI model licenses for commercial use.

---

<div align="center">

** If you like the project, don't forget to give it a star!**

Made with  and 

</div>
