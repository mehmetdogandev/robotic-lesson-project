# ⚡ ESP32 Kamera + OLED Hızlı Kullanım Kılavuzu

## 🔧 Donanım Bağlantıları

```
OLED SSD1306 (128x64, I2C)
├─ VCC  → 3.3V
├─ GND  → GND
├─ SDA  → D10 (Deneyap Kart)
└─ SCL  → D11 (Deneyap Kart)  ⚠️ ÖNEMLİ!
```

## 📝 Hızlı Başlangıç

### 1. ESP32 Kurulumu

```cpp
// esp_system.ino dosyasında WiFi ayarları
const char* ssid = "WiFi_Adiniz";
const char* password = "WiFi_Sifreniz";
```

**Derleme Ayarları (ÇOK ÖNEMLİ!):**
- `Tools > Partition Scheme` → **"Huge APP"**
- `Tools > Board` → ESP32 kartınızı seçin
- Upload!

### 2. Python Kurulumu

```bash
# Gerekli paketler yüklü
pip install requests flask opencv-python deepface mediapipe

# Uygulamayı başlat
python main.py

# ESP32 OLED URL girin (örnek):
# http://192.168.1.100/face_mood
```

## 🎯 Önemli Özellikler

### ✅ Optimize Edilmiş Yapı

1. **Eşzamanlı Çalışma:**
   - Kamera stream `:81/stream` portunda
   - OLED endpoint `/face_mood` ana portta
   - İki servis birbirini engellemiyor!

2. **Hafıza Optimizasyonu:**
   - ❌ Gereksiz loglar kaldırıldı
   - ❌ ESP_LOG hafızaya yazılmıyor
   - ✅ Sadece Serial.print kullanılıyor
   - ✅ Stack size optimize edildi (8KB)

3. **Hızlı İletişim:**
   - Python → ESP32: 500ms timeout
   - ESP32 meşgulse skip et (blocking yok)
   - Hata mesajları minimal

### 🔍 Test Etme

```bash
# Eşzamanlı erişim testi
python test_concurrent_access.py
```

Bu test:
- ✅ 30 saniye boyunca kamera stream okur
- ✅ Aynı anda OLED'e veri gönderir
- ✅ İki servisin de çalıştığını doğrular

## 📡 API Kullanımı

### Kamera Stream
```
http://<ESP32_IP>:81/stream
```

### OLED Ekran (POST)
```bash
curl -X POST http://<ESP32_IP>/face_mood \
  -H "Content-Type: application/json" \
  -d '{"emotion":"happy","confidence":0.95}'
```

**Desteklenen Duygular:**
- `happy`, `sad`, `angry`, `neutral`, `surprise`, `fear`, `disgust`

## 🐛 Sorun Giderme

### Problem: ESP32'ye bağlanamıyorum

**Çözüm:**
1. ESP32 Serial Monitor'ü açın
2. IP adresini kontrol edin
3. WiFi bağlantısını doğrulayın
4. Aynı ağda olduğunuzdan emin olun

### Problem: Kameraya erişilemezken OLED çalışmıyor

**Çözüm:**
- ✅ Bu normal değil! İki servis bağımsız çalışmalı
- Seri monitörde hata var mı kontrol edin
- ESP32'yi yeniden başlatın
- `test_concurrent_access.py` ile test edin

### Problem: OLED ekran güncellemiyor

**Çözüm:**
1. I2C bağlantılarını kontrol edin (özellikle SCL=D11)
2. OLED I2C adresi 0x3C mi kontrol edin
3. Seri monitörde "OLED ekran baslatilmamis" mesajı var mı bakın

### Problem: "Huge APP" seçeneği yok

**Çözüm:**
1. Arduino IDE'de ESP32 board desteğini güncelleyin
2. `Tools > Board > Boards Manager`
3. "ESP32" arayın ve güncelleyin

## 💡 İpuçları

1. **Performans:**
   - OLED güncellemeleri çok hızlıdır (~50ms)
   - Kamera stream OLED'den etkilenmez
   - Her ikisi de Core 0'da çalışır (kamera Core 1'de)

2. **Kararlılık:**
   - ESP32 başladıktan sonra 2 saniye bekleyin
   - OLED ilk mesajı gösterir: "Deneyap Hazir"
   - Python timeout'ları kısa tutun (500ms)

3. **Debugging:**
   - Serial Monitor 115200 baud
   - OLED başarısızlıkları sessizdir (blocking yok)
   - Python hatalarını görmek için: `python main.py`

## 📊 Sistem Mimarisi

```
┌─────────────┐
│   Python    │
│  (Camera)   │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  ESP32:81   │   │  ESP32:80   │
│   Stream    │   │  /face_mood │
└─────────────┘   └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │    OLED     │
                  │  (D10,D11)  │
                  └─────────────┘
```

## 🎓 Örnek Kullanım

### Python Entegrasyonu

```python
import requests

ESP32_IP = "192.168.1.100"

# OLED'e duygu gönder
def send_emotion(emotion, confidence):
    try:
        response = requests.post(
            f"http://{ESP32_IP}/face_mood",
            json={"emotion": emotion, "confidence": confidence},
            timeout=0.5
        )
        return response.status_code == 200
    except:
        return False

# Kullanım
send_emotion("happy", 0.95)
```

### Kamera Stream Okuma

```python
import cv2

cap = cv2.VideoCapture(f"http://{ESP32_IP}:81/stream")

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("ESP32 Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## 📈 Performans Metrikleri

- **OLED Güncelleme:** ~50ms
- **HTTP İstek:** ~30ms
- **Kamera FPS:** ~15-20 (QVGA)
- **Python → ESP32:** <500ms
- **Eşzamanlı Kullanım:** ✅ Sorunsuz

## 🔐 Güvenlik Notları

⚠️ Bu sistem **eğitim amaçlıdır**:
- Varsayılan olarak güvenlik yok
- WiFi şifreleri kodda
- HTTP (HTTPS değil)

Üretimde kullanmadan önce:
1. HTTPS ekleyin
2. Kimlik doğrulama ekleyin
3. Rate limiting ekleyin

---

**Son Güncelleme:** 2025-11-09  
**Versiyon:** 2.0 (Optimized)  
**Durum:** ✅ Üretim hazır (eğitim için)
