# ESP32 Kamera Ayarları - Duygu Analizi Optimizasyonu

## 🎯 Optimal Ayarlar (Önceden Tanımlı Preset)

Duygu analizi için en iyi sonuçları elde etmek amacıyla aşağıdaki ayarlar önerilir:

### Temel Görüntü Ayarları

| Parametre    | Değer | Açıklama                                           |
|--------------|-------|----------------------------------------------------|
| framesize    | 8     | XGA (1024x768) - Yüz tespiti için ideal denge     |
| quality      | 10    | En iyi JPEG kalitesi                               |
| brightness   | 0     | Varsayılan parlaklık (ortam aydınlatmasına göre)  |
| contrast     | 0     | Varsayılan kontrast (yüz özelliklerini korur)     |
| saturation   | 0     | Doğal renk doygunluğu (cilt tonu tespiti için)    |

### Otomatik Ayarlar (KRİTİK!)

| Parametre    | Değer | Açıklama                                           |
|--------------|-------|----------------------------------------------------|
| awb          | 1     | ✅ Auto White Balance AÇIK - Doğru yüz analizi için kritik |
| awb_gain     | 1     | ✅ AWB gain AÇIK                                   |
| aec          | 1     | ✅ Auto Exposure AÇIK                              |
| aec2         | 1     | ✅ DSP tabanlı exposure AÇIK                       |
| ae_level     | 0     | Varsayılan exposure seviyesi                       |
| agc          | 1     | ✅ Auto Gain AÇIK                                  |
| gainceiling  | 2     | Orta gain ceiling (gürültüyü azaltır)             |

### Görüntü Düzeltme

| Parametre    | Değer | Açıklama                                           |
|--------------|-------|----------------------------------------------------|
| bpc          | 1     | ✅ Black Pixel Correction AÇIK                     |
| wpc          | 1     | ✅ White Pixel Correction AÇIK                     |
| raw_gma      | 1     | ✅ Raw gamma AÇIK (daha iyi dinamik aralık)        |
| lenc         | 1     | ✅ Lens düzeltme AÇIK                              |

### Geometrik Ayarlar

| Parametre    | Değer | Açıklama                                           |
|--------------|-------|----------------------------------------------------|
| hmirror      | 0     | Yatay aynalama KAPALI                              |
| vflip        | 0     | Dikey çevirme KAPALI                               |
| dcw          | 1     | Downsize AÇIK (performans için)                    |

### Yüz Algılama

| Parametre    | Değer | Açıklama                                           |
|--------------|-------|----------------------------------------------------|
| face_detect  | 1     | ✅ ESP32'de yüz algılama AÇIK                      |

---

## 📊 Çözünürlük Seçenekleri

| framesize | Çözünürlük       | Kullanım Senaryosu                    | FPS    |
|-----------|------------------|---------------------------------------|--------|
| 10        | UXGA (1600x1200) | En yüksek detay (yavaş)               | ~5     |
| 9         | SXGA (1280x1024) | Yüksek detay                          | ~8     |
| **8** ⭐   | **XGA (1024x768)** | **Duygu analizi için OPTIMAL**      | ~15    |
| 7         | SVGA (800x600)   | İyi denge                             | ~20    |
| 6         | VGA (640x480)    | Hızlı işleme                          | ~30    |
| 5         | CIF (352x288)    | Çok hızlı (düşük detay)               | ~40    |
| 4         | QVGA (320x240)   | Minimum detay                         | ~50    |

**⭐ Tavsiye:** XGA (1024x768) duygu analizi için en iyi denge sunar:
- Yüz özelliklerini yeterince detaylı yakalar
- Makul FPS sağlar (~15-20 fps)
- Python tarafında işleme hızı kabul edilir
- Ağ bant genişliğini optimize eder

---

## 🎨 JPEG Kalite (quality parametresi)

| Değer  | Kalite        | Kullanım                                |
|--------|---------------|-----------------------------------------|
| 10     | En Yüksek ⭐  | Duygu analizi için önerilen             |
| 12     | Çok İyi       | İyi alternatif                          |
| 15     | İyi           | Hızlı ağlar için                        |
| 20-30  | Orta          | Bant genişliği sınırlıysa               |
| 40-63  | Düşük         | Tavsiye edilmez                         |

**Not:** Düşük değer = yüksek kalite. 10 en iyi kalitedir.

---

## 🔧 Manuel Ayar Rehberi

### 1. Parlaklık (brightness: -2 ile +2)
- **0:** Varsayılan (çoğu durum için uygun)
- **+1, +2:** Karanlık ortamlar için
- **-1, -2:** Çok aydınlık ortamlar için

### 2. Kontrast (contrast: -2 ile +2)
- **0:** Varsayılan (yüz özellikleri için ideal)
- **+1:** Düşük kontrastlı ortamlar
- **-1:** Aşırı kontrastlı durumlarda

### 3. Doygunluk (saturation: -2 ile +2)
- **0:** Doğal renkler (cilt tonu tespiti için en iyi)
- **+1, +2:** Soluk görüntüler için
- **-1, -2:** Aşırı doygun renkler için

### 4. Gain Ceiling (gainceiling: 0-6)
- **0:** 2x
- **1:** 4x
- **2:** 8x ⭐ (önerilen - dengeli)
- **3:** 16x
- **4:** 32x
- **5:** 64x
- **6:** 128x (çok fazla gürültü)

---

## ⚡ Özel Efektler (special_effect)

| Değer | Efekt         | Duygu Analizi İçin    |
|-------|---------------|----------------------|
| 0     | Yok           | ✅ Önerilen          |
| 1     | Negatif       | ❌ Kullanma          |
| 2     | Gri Tonlama   | ⚠️ Test için olabilir |
| 3     | Kırmızı Ton   | ❌ Kullanma          |
| 4     | Yeşil Ton     | ❌ Kullanma          |
| 5     | Mavi Ton      | ❌ Kullanma          |
| 6     | Sepia         | ❌ Kullanma          |

---

## 🚨 Yaygın Sorunlar ve Çözümler

### Problem: Yüzler çok karanlık
**Çözüm:**
```
brightness = +1 veya +2
aec = 1 (otomatik exposure açık olmalı)
ae_level = +1
```

### Problem: Yüzler aşırı parlak (ışık yanması)
**Çözüm:**
```
brightness = -1 veya -2
ae_level = -1
gainceiling = 1 (gain'i düşür)
```

### Problem: Renkler yanlış (sarı/mavi ton)
**Çözüm:**
```
awb = 1 (MUTLAKA AÇIK OLMALI!)
awb_gain = 1
wb_mode = 0 (otomatik)
```

### Problem: Görüntü bulanık
**Çözüm:**
```
framesize = 8 veya daha yüksek
quality = 10
lenc = 1 (lens düzeltme)
```

### Problem: Düşük FPS
**Çözüm:**
```
framesize = 6 veya 7 (çözünürlüğü düşür)
quality = 12 veya 15
face_detect = 0 (ESP'deki yüz algılamayı kapat)
```

### Problem: Gürültülü görüntü (karanlık ortam)
**Çözüm:**
```
gainceiling = 2 (yükseltme, ama çok değil)
bpc = 1 (black pixel correction)
wpc = 1 (white pixel correction)
raw_gma = 1
```

---

## 📝 Kullanım Örnekleri

### Frontend'den Optimizasyon
```javascript
// Otomatik optimal ayarları uygula
await fetch('/esp_apply_preset', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ ip: '10.158.242.195' })
});
```

### Manuel Parametre Değiştirme
```javascript
// Parlaklığı artır
await fetch('/esp_command', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ 
        ip: '10.158.242.195',
        params: { var: 'brightness', val: '1' }
    })
});
```

### Python'dan Doğrudan Kullanım
```python
from modules import esp_client

# Optimal ayarları uygula
esp_client.apply_emotion_analysis_preset('10.158.242.195')

# Tek parametre değiştir
esp_client.send_command('10.158.242.195', {'var': 'brightness', 'val': '1'})

# Mevcut ayarları oku
status, settings = esp_client.get_status('10.158.242.195')
print(settings)
```

---

## 🎓 İpuçları

1. **İlk bağlantıda** "Duygu Analizi İçin Optimize Et" butonuna basın
2. **Aydınlatma değişirse** sadece brightness ve ae_level'ı ayarlayın
3. **Renkler yanlışsa** AWB'nin açık olduğundan emin olun
4. **Hız önemliyse** çözünürlüğü düşürün (framesize = 6-7)
5. **Kalite önemliyse** çözünürlüğü ve quality'yi artırın
6. **Test yaparken** her değişiklikten sonra birkaç saniye bekleyin

---

## ⚙️ API Referansı

### `/esp_command` (POST)
ESP'ye komut gönder
```json
{
    "ip": "10.158.242.195",
    "params": {
        "var": "framesize",
        "val": "8"
    }
}
```

### `/esp_status` (GET)
Mevcut ayarları oku
```
GET /esp_status?ip=10.158.242.195
```

### `/esp_apply_preset` (POST)
Optimal ayarları uygula
```json
{
    "ip": "10.158.242.195"
}
```

---

**Not:** Bu ayarlar OV2640/OV5640 kamera modülleri için test edilmiştir. Farklı kamera modelleri için bazı parametreler değişebilir.
