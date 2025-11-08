

"""
Flask Web Application - Main file
Face recognition and emotion detection system
"""
from flask import Flask, render_template, Response, jsonify, request
from modules.config import latest_state
from modules.camera import camera_stream
from modules.storage import load_existing_faces, get_captured_images

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
    return Response(camera_stream.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/captured')
def get_captured():
    """Lists captured dangerous person files."""
    images = get_captured_images()
    return jsonify(images)


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
