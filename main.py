

"""
Flask Web Uygulaması - Ana dosya
Yüz tanıma ve emotion detection sistemi
"""
from flask import Flask, render_template, Response, jsonify, request
from modules.config import latest_state
from modules.camera import camera_stream
from modules.storage import load_existing_faces, get_captured_images

app = Flask(__name__)

# Uygulama başlarken kayıtlı kişileri yükle
load_existing_faces()




# ============================================
# Flask Route'ları
# ============================================

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video stream endpoint'i"""
    return Response(camera_stream.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/captured')
def get_captured():
    """Kaydedilen tehlikeli kişi dosyalarını listeler."""
    images = get_captured_images()
    return jsonify(images)


@app.route('/set_detection', methods=['POST'])
def set_detection():
    """Algılama aç/kapat."""
    try:
        payload = request.get_json(silent=True) or {}
        enabled = payload.get('enabled')
        
        if isinstance(enabled, bool):
            camera_stream.set_detection(enabled)
            return jsonify({"enabled": camera_stream.is_detection_enabled()}), 200
        
        return jsonify({"error": "'enabled' (bool) bekleniyor"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/status')
def status():
    """Algılama durumunu döndürür."""
    return jsonify({"enabled": camera_stream.is_detection_enabled()})


@app.route('/current_emotions')
def current_emotions():
    """Güncel emotion verilerini döndürür."""
    data = {
        "enabled": camera_stream.is_detection_enabled(),
        "timestamp": latest_state.get("timestamp"),
        "emotions": latest_state.get("emotions"),
        "main_emotion": latest_state.get("main_emotion"),
        "danger_score": latest_state.get("danger_score"),
    }
    return jsonify(data)



# ============================================
# Uygulama Başlatma
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Yüz Tanıma ve Emotion Detection Sistemi")
    print("=" * 60)
    print("✓ Modüller yüklendi")
    print("✓ Kayıtlı kişiler hafızaya alındı")
    print("🌐 Uygulama başlatılıyor: http://0.0.0.0:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
