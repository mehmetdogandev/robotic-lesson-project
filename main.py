from flask import Flask, render_template, Response, jsonify
from modules.camera import generate_frames, DETECTION_ENABLED, latest_state
from modules.storage import load_existing_faces

app = Flask(__name__)

# Kayıtlı tehlikeli kişileri yükle
load_existing_faces()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({"enabled": DETECTION_ENABLED})

@app.route('/current_emotions')
def current_emotions():
    return jsonify(latest_state)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
