# ESP32 OLED Duygu Durumu Gösterimi

Bu sistem, Python tarafındaki yüz tanıma ve duygu analizi sonuçlarını ESP32'ye bağlı bir OLED ekranda gerçek zamanlı olarak görüntüler.

## 🔧 Donanım Gereksinimleri

- **Deneyap Geliştirme Kartı** (ESP32 tabanlı, kamera modülü dahili)
- **SSD1306 OLED Ekran** (128x64, I2C)
- **Bağlantılar:**
  - OLED SDA → Deneyap D10
  - OLED SCL → Deneyap D5
  - OLED VCC → 3.3V
  - OLED GND → GND

## 📚 Kütüphane Gereksinimleri

Arduino IDE'de aşağıdaki kütüphaneleri yüklemelisiniz:

1. **Adafruit GFX Library**
2. **Adafruit SSD1306**
3. **Wire** (Arduino ile birlikte gelir)

## 🚀 Kurulum

### ESP32 Tarafı

1. **Arduino IDE Ayarları:**
   - `Tools > Board` → ESP32 kartınızı seçin
   - `Tools > Partition Scheme` → **"Huge APP"** seçin (ÖNEMLİ!)
   - Port ayarını yapın

2. **WiFi Ayarları:**
   - `esp_system.ino` dosyasını açın
   - `ssid` ve `password` değişkenlerini kendi WiFi ağınıza göre düzenleyin:
   ```cpp
   const char* ssid = "WiFi_Adiniz";
   const char* password = "WiFi_Sifreniz";
   ```

3. **Yükleme:**
   - Kodu ESP32'ye yükleyin
   - Seri monitörü açın (115200 baud)
   - ESP32'nin IP adresini not edin

### Python Tarafı

1. **Gerekli Python Paketleri:**
   ```bash
   pip install requests
   ```

2. **Uygulama Başlatma:**
   ```bash
   python main.py
   ```

3. **ESP32 OLED URL Girişi:**
   - Uygulama başlarken size ESP32 OLED URL'si sorulacak
   - Format: `http://<ESP32_IP_ADRESI>/face_mood`
   - Örnek: `http://192.168.1.100/face_mood`
   - Boş bırakırsanız OLED gösterimi devre dışı kalır

## 📡 API Endpoint'leri

### `/face_mood` (POST)
ESP32'ye duygu durumu gönderir.

**İstek Formatı:**
```json
{
  "emotion": "happy",
  "confidence": 0.95
}
```

**Desteklenen Duygular:**
- `happy` → Mutlu
- `sad` → Üzgün
- `angry` → Kızgın
- `neutral` → Nötr
- `surprise` → Şaşkın
- `fear` → Korkmuş
- `disgust` → Tiksinmiş

**Yanıt:**
```json
{
  "status": "success",
  "message": "Emotion displayed on OLED"
}
```

## 🖥️ OLED Ekran Görünümü

Ekran üzerinde şunlar gösterilir:

```
┌────────────────────┐
│ Duygu Durumu:      │
├────────────────────┤
│                    │
│      Mutlu         │  ← Büyük font, ortalanmış
│                    │
│   Güven: 95.0%     │  ← Güven skoru
│ ▓▓▓▓▓▓▓▓▓▓▓░░░░░  │  ← Görsel çubuk
└────────────────────┘
```

## 🔄 Çalışma Akışı

1. **Python Uygulaması:**
   - Kameradan yüz algılar
   - Duygu analizi yapar
   - Sonuçları ESP32'ye gönderir

2. **ESP32:**
   - HTTP POST isteğini alır
   - JSON verisini parse eder
   - OLED ekranda gösterir

3. **OLED Ekran:**
   - Duygu durumunu Türkçe gösterir
   - Güven skorunu yüzde olarak gösterir
   - Görsel çubukla güven seviyesini gösterir

## 🛠️ Sorun Giderme

### ESP32 WiFi'ye Bağlanmıyor
- SSID ve şifrenizi kontrol edin
- WiFi sinyal gücünü kontrol edin
- Seri monitörde hata mesajlarını kontrol edin

### OLED Ekran Çalışmıyor
- I2C bağlantılarını kontrol edin (SDA=D10, SCL=D5)
- OLED I2C adresinin 0x3C olduğunu doğrulayın
- Wire.begin() fonksiyonunun doğru pinlerle çağrıldığını kontrol edin

### Python'dan Veri Gelmiyor
- ESP32 IP adresini doğru girdiğinizden emin olun
- Her iki cihazın da aynı ağda olduğunu kontrol edin
- Firewall ayarlarını kontrol edin
- ESP32 seri monitöründe gelen istekleri kontrol edin

### Derleme Hataları
- "Huge APP" partition scheme seçildiğinden emin olun
- Tüm kütüphanelerin yüklü olduğunu kontrol edin
- Arduino IDE'nin güncel olduğundan emin olun

## 📝 Notlar

- OLED ekran güncellemeleri anlık olarak gerçekleşir
- Sistem, düşük gecikme için optimize edilmiştir
- Türkçe karakterler için özel kodlama kullanılmıştır
- Maksimum 128x64 piksel çözünürlük desteklenir

## 🔗 Bağlantılar

- **Kamera Stream:** `http://<ESP32_IP>:81/stream`
- **Duygu Endpoint:** `http://<ESP32_IP>/face_mood`
- **Durum Kontrolü:** `http://<ESP32_IP>/status`

## 📄 Lisans

Bu proje Apache License 2.0 altında lisanslanmıştır (Espressif Systems kod tabanı için).

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen pull request gönderin veya issue açın.

---

**Not:** Bu sistem eğitim amaçlıdır. Üretim ortamında kullanmadan önce güvenlik testlerini yapın.
