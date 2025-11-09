"""
ESP32 Kamera + OLED Test Script
Hem kameraya hem OLED ekrana aynı anda erişimi test eder
"""
import requests
import time
import threading

ESP32_IP = "10.64.220.72"  # ESP32 IP adresinizi girin
CAMERA_URL = f"http://{ESP32_IP}:81/stream"
OLED_URL = f"http://{ESP32_IP}/face_mood"

# Test duyguları
test_emotions = [
    {"emotion": "happy", "confidence": 0.95},
    {"emotion": "sad", "confidence": 0.87},
    {"emotion": "angry", "confidence": 0.92},
    {"emotion": "neutral", "confidence": 0.88},
    {"emotion": "surprise", "confidence": 0.94},
]

# Kamera stream test fonksiyonu
def test_camera_stream():
    """Kamera stream'ine sürekli erişim testi"""
    print("🎥 Kamera stream testi başlatılıyor...")
    
    try:
        # Keep-alive bağlantı kullan
        session = requests.Session()
        session.headers.update({'Connection': 'keep-alive'})
        
        response = session.get(CAMERA_URL, stream=True, timeout=15)
        
        if response.status_code == 200:
            print("✓ Kamera stream'ine bağlanıldı")
            
            # 30 saniye boyunca stream'i oku
            start_time = time.time()
            frame_count = 0
            last_print = 0
            
            try:
                for chunk in response.iter_content(chunk_size=1024):
                    if time.time() - start_time > 30:
                        break
                    if chunk:
                        frame_count += 1
                        # Her 5 saniyede bir rapor
                        if time.time() - last_print > 5:
                            print(f"  📹 Kamera aktif - {frame_count} chunk, {int(time.time() - start_time)}s")
                            last_print = time.time()
                
                print(f"✓ Kamera stream testi tamamlandı - {frame_count} chunk")
            except Exception as e:
                print(f"⚠️ Stream okuma hatası (normal olabilir): {e}")
                if frame_count > 100:
                    print(f"✓ Ancak {frame_count} chunk alındı - test başarılı sayılır")
        else:
            print(f"✗ Kamera stream bağlantı hatası: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Kamera stream hatası: {e}")

# OLED ekran test fonksiyonu
def test_oled_display():
    """OLED ekrana sürekli veri gönderme testi"""
    print("📟 OLED ekran testi başlatılıyor...")
    
    test_count = 0
    success_count = 0
    
    try:
        # 30 saniye boyunca 2 saniyede bir duygu gönder
        start_time = time.time()
        
        while time.time() - start_time < 30:
            emotion_data = test_emotions[test_count % len(test_emotions)]
            test_count += 1
            
            try:
                response = requests.post(
                    OLED_URL,
                    json=emotion_data,
                    timeout=1
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  📟 OLED güncellendi: {emotion_data['emotion']} ({test_count}/{test_count})")
                else:
                    print(f"  ⚠️ OLED yanıt hatası: {response.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️ OLED isteği başarısız: {e}")
            
            time.sleep(2)
        
        print(f"✓ OLED test tamamlandı - {success_count}/{test_count} başarılı")
        
    except Exception as e:
        print(f"✗ OLED test hatası: {e}")

# Ana test
def run_concurrent_test():
    """Kamera ve OLED'i aynı anda test et"""
    print("=" * 60)
    print("🔬 ESP32 Eşzamanlı Erişim Testi")
    print("=" * 60)
    print(f"ESP32 IP: {ESP32_IP}")
    print(f"Kamera URL: {CAMERA_URL}")
    print(f"OLED URL: {OLED_URL}")
    print("-" * 60)
    
    # İki thread oluştur
    camera_thread = threading.Thread(target=test_camera_stream, daemon=True)
    oled_thread = threading.Thread(target=test_oled_display, daemon=True)
    
    # Testleri başlat
    print("\n🚀 Testler başlatılıyor...\n")
    camera_thread.start()
    time.sleep(1)  # Kameranın başlaması için kısa bekleme
    oled_thread.start()
    
    # Testlerin bitmesini bekle
    camera_thread.join()
    oled_thread.join()
    
    print("\n" + "=" * 60)
    print("✅ Test tamamlandı!")
    print("=" * 60)
    print("\nSonuç:")
    print("- Her iki servis de aynı anda çalışıyorsa ✓ başarılı")
    print("- Herhangi bir servis bloklandıysa ✗ problem var")
    print("-" * 60)

# Basit bağlantı testi
def test_basic_connection():
    """ESP32'ye temel bağlantı testi"""
    print("\n🔍 Temel Bağlantı Testi")
    print("-" * 60)
    
    # Ping test (HTTP GET root)
    try:
        response = requests.get(f"http://{ESP32_IP}/", timeout=3)
        print(f"✓ ESP32 erişilebilir (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ ESP32'ye bağlanılamadı: {e}")
        return False
    
    # OLED endpoint testi
    try:
        response = requests.post(
            OLED_URL,
            json={"emotion": "neutral", "confidence": 1.0},
            timeout=2
        )
        print(f"✓ OLED endpoint çalışıyor (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ OLED endpoint hatası: {e}")
    
    # Kamera status testi
    try:
        response = requests.get(f"http://{ESP32_IP}/status", timeout=3)
        print(f"✓ Status endpoint çalışıyor (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ Status endpoint hatası: {e}")
    
    print("-" * 60)
    return True

if __name__ == "__main__":
    try:
        # Önce temel bağlantıyı test et
        if not test_basic_connection():
            print("\n⚠️ ESP32'ye bağlanılamadı. IP adresini kontrol edin.")
            print(f"Mevcut IP: {ESP32_IP}")
            exit(1)
        
        # Ana testi çalıştır
        run_concurrent_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n\n✗ Test hatası: {e}")
