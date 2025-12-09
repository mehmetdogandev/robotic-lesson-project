# Yaş Tahmini Modülü - Kullanım Kılavuzu

## 🎯 Genel Bakış

Yaş tahmini modülü, mevcut duygu analizi sistemine **modüler** bir şekilde eklenmiştir. Sistemin çalışmasını etkilemeden yaş tahmini yapabilir ve bu bilgiyi tehlikeli kişi kayıtlarına ekler.

## ✨ Yeni Özellikler

### 1. **Yaş Tahmini**

- DeepFace kütüphanesi kullanılarak gerçek zamanlı yaş tahmini
- Temporal smoothing ile daha kararlı sonuçlar
- Yaş kategorileri: Çocuk, Genç, Yetişkin, Orta Yaşlı, Yaşlı

### 2. **Modüler Yapı**

- `modules/age_detection.py` - Bağımsız yaş tahmini modülü
- Mevcut kod tabanını bozmadan eklenmiştir
- Kolayca açılıp kapatılabilir

### 3. **Performans Optimizasyonu**

- Yaş tahmini, duygu analizinden daha az sıklıkta çalışır (performans için)
- Temporal smoothing ile hassas sonuçlar
- Background thread kullanımı ile UI engellenmez

## 📁 Yeni Dosyalar

```
modules/
  └── age_detection.py        # Yaş tahmini modülü (YENİ)
```

## 🔧 Yapılandırma

### config.py'de Yeni Ayarlar

```python
# Yaş tahmini ayarları
AGE_DETECTION_ENABLED = True  # Yaş tahminini aç/kapat
AGE_SMOOTHING_WINDOW = 5      # Temporal smoothing için frame sayısı
```

### latest_state Güncellemeleri

```python
latest_state = {
    "timestamp": None,
    "emotions": None,
    "main_emotion": None,
    "danger_score": 0.0,
    "age": None,              # YENİ
    "age_category": None,     # YENİ
}
```

## 🚀 Kullanım

### 1. API Endpoint'i

```javascript
// /current_emotions endpoint'i artık yaş bilgisini de döndürür
{
    "enabled": true,
    "timestamp": "20241209-143022",
    "emotions": {...},
    "main_emotion": "happy",
    "danger_score": 15.5,
    "age": 28,                    // YENİ
    "age_category": "Yetişkin"    // YENİ
}
```

### 2. Tehlikeli Kişi Kaydı

JSON dosyasına yaş bilgisi de eklenir:

```json
{
    "id": "abc123",
    "timestamp": "20241209-143022",
    "emotions": {...},
    "age": 28,
    "age_category": "Yetişkin"
}
```

### 3. Web Arayüzü

- **Canlı video**: Yaş bilgisi video üzerinde görüntülenir
- **Anlık duygular paneli**: Yaş ve kategori gösterilir
- **Galeri kartları**: Kayıtlı kişilerin yaşları görünür

## 📊 Yaş Kategorileri

| Yaş Aralığı | Kategori   |
| ----------- | ---------- |
| 0-12        | Çocuk      |
| 13-19       | Genç       |
| 20-39       | Yetişkin   |
| 40-59       | Orta Yaşlı |
| 60+         | Yaşlı      |

## 🔬 Teknik Detaylar

### Yaş Tahmini Algoritması

```python
def analyze_age(rgb_frame):
    """
    1. DeepFace ile yaş tahmini
    2. Temporal smoothing (median filter)
    3. Kategori belirleme
    """
    age = estimate_age(rgb_frame)
    smoothed_age = age_estimator.update(age)
    category = get_age_category(smoothed_age)
    return smoothed_age, category
```

### Performans İyileştirmeleri

- **Frame skipping**: Yaş analizi her 6 frame'de bir yapılır
- **Temporal smoothing**: Son 5 frame'in medyanı alınır
- **Lazy initialization**: Modül sadece gerektiğinde yüklenir
- **Error handling**: Yaş tahmini başarısız olursa sistem çalışmaya devam eder

## 🎨 UI Güncellemeleri

### Video Üzerinde Gösterim

```
Baskin Duygu: Mutlu (85.3%)
Yas: 28 (Yetişkin)              ← YENİ
```

### Anlık Duygular Paneli

```
Mutlu
⏰ 14:30:22 • ⚠ Tehlike: 15.5% • 👤 Yaş: 28 (Yetişkin)
```

### Galeri Kartları

```
ID: abc123  [Mutlu]
⏰ 20241209-143022 • 🛡 Tehlike: 15.5% • 👤 Yaş: 28 (Yetişkin)
```

## ⚙️ Yapılandırma Seçenekleri

### Yaş Tahminini Kapatma

```python
# config.py
AGE_DETECTION_ENABLED = False
```

### Smoothing Ayarı

```python
# config.py
AGE_SMOOTHING_WINDOW = 7  # Daha smooth (yavaş tepki)
AGE_SMOOTHING_WINDOW = 3  # Daha responsive (hızlı tepki)
```

## 🐛 Hata Ayıklama

### Yaş tahmini çalışmıyor?

1. **DeepFace yüklü mü?** - `pip install deepface`
2. **AGE_DETECTION_ENABLED True mu?** - `config.py`'yi kontrol edin
3. **Yüz algılanıyor mu?** - Video akışında yüz mesh'i görünüyor olmalı

### Performans sorunları?

1. **Frame interval artırın**: `ANALYSIS_INTERVAL` değerini yükseltin
2. **Smoothing window azaltın**: `AGE_SMOOTHING_WINDOW` değerini düşürün
3. **Yaş tahminini kapatın**: `AGE_DETECTION_ENABLED = False`

## 📈 Gelecek İyileştirmeler

- [ ] Cinsiyet tahmini ekleme
- [ ] Yaş aralığı gösterimi (örn: 25-30)
- [ ] Yaş-duygu korelasyon analizi
- [ ] Daha hızlı yaş tahmini modelleri
- [ ] Batch processing desteği

## 🎓 Örnek Kullanım Senaryoları

### 1. Güvenlik Uygulaması

```python
if age < 18 and danger_score > 70:
    alert("Çocuk tehlikede!")
```

### 2. İstatistik Toplama

```python
age_distribution = {
    "Çocuk": 5,
    "Genç": 15,
    "Yetişkin": 45,
    "Orta Yaşlı": 25,
    "Yaşlı": 10
}
```

### 3. Kişiselleştirilmiş Hizmet

```python
if age_category == "Yaşlı":
    increase_font_size()
    simplify_interface()
```

## 📝 Notlar

- Yaş tahmini %100 doğru değildir, bir tahmindir
- Yüz kalitesi ve ışık koşulları sonucu etkiler
- Temporal smoothing doğruluğu artırır
- Sistem, yaş tahmini başarısız olsa bile çalışmaya devam eder

## 🤝 Katkıda Bulunma

Yaş tahmini modülünü geliştirmek için:

1. `modules/age_detection.py` dosyasını düzenleyin
2. Test edin
3. Pull request gönderin

---

**Son Güncelleme**: 9 Aralık 2025
**Versiyon**: 1.0.0
**Geliştirici**: AI Assistant with Human Collaboration
