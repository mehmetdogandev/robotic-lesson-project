# 🚀 ESP32 Kamera Hızlı Başlangıç Kılavuzu

## 📋 Gereksinimler
- ✅ ESP32-CAM modülü (yüklenmiş firmware ile)
- ✅ Aynı ağda bilgisayar ve ESP32
- ✅ ESP32'nin IP adresi

## 🎯 3 Adımda Kullanıma Başlayın

### 1️⃣ Bağlantı Kurun
```
1. Web arayüzünü açın: http://localhost:5000
2. IP giriş kutusuna ESP32'nin IP adresini yazın
   Örnek: 10.64.220.72
3. "Bağlan" butonuna tıklayın
4. Video akışı ESP32'den gelmeye başlayacak
```

### 2️⃣ Optimal Ayarları Uygulayın
```
1. ESP32'ye bağlandıktan sonra otomatik olarak 
   "ESP32 Kamera Ayarları" paneli açılacak
2. "✨ Duygu Analizi İçin Optimize Et" butonuna tıklayın
3. Sistem en iyi ayarları otomatik olarak uygulayacak
4. 5-10 saniye bekleyin (ayarlar uygulanıyor)
```

### 3️⃣ Duygu Analizi Başlatın
```
1. "Algılamayı Aç" butonuna tıklayın
2. Kamera önüne geçin
3. Anlık duygular sağ panelde gösterilecek
4. Tehlikeli durum tespit edilirse otomatik kayıt yapılacak
```

## ⚙️ Optimal Ayarlar (Otomatik Uygulanır)

| Ayar | Değer | Neden? |
|------|-------|--------|
| Çözünürlük | XGA (1024x768) | Yüz detayları için ideal |
| JPEG Kalite | 10 (en yüksek) | Net görüntü |
| Auto White Balance | ✅ Açık | Doğru cilt tonu |
| Auto Exposure | ✅ Açık | Uygun aydınlatma |
| Auto Gain | ✅ Açık | Düşük ışıkta iyileştirme |
| Lens Correction | ✅ Açık | Distorsiyon düzeltme |

## 🔧 Manuel Ayarlar (İsteğe Bağlı)

### Parlaklık Ayarı
- **Karanlık ortam:** +1 veya +2
- **Aydınlık ortam:** -1 veya -2
- **Normal:** 0 (varsayılan)

### Çözünürlük Değiştirme
- **Yüksek detay gerek:** SXGA/UXGA (yavaş)
- **Denge:** XGA (önerilen) ⭐
- **Hızlı işlem:** VGA/SVGA

### Özel Efektler
- **Normal kullanım:** Yok (önerilen)
- **Test:** Gri Tonlama
- **Duygu analizi için:** Efekt kullanmayın!

## ⚠️ Yaygın Sorunlar

### ❌ "Bağlantı Hatası"
**Çözüm:**
1. ESP32'nin açık olduğundan emin olun
2. IP adresini kontrol edin
3. Aynı WiFi ağında olduğunuzu doğrulayın
4. Ping testi: `ping 10.64.220.72`

### ❌ Görüntü Çok Karanlık
**Çözüm:**
1. Parlaklık kontrolünü +1 veya +2 yapın
2. Auto Exposure'ın açık olduğunu kontrol edin
3. Ortam ışığını artırın

### ❌ Renkler Yanlış (Sarı/Mavi Ton)
**Çözüm:**
1. Auto White Balance'ı kontrol edin (MUTLAKA AÇIK)
2. "Optimal Ayarlar" butonuna tekrar basın
3. Birkaç saniye bekleyin (AWB ayarlanıyor)

### ❌ Görüntü Kasıyor / Yavaş
**Çözüm:**
1. Çözünürlüğü VGA veya SVGA'ya düşürün
2. JPEG kalitesini 15-20 arası yapın
3. WiFi sinyalini güçlendirin

### ❌ Yüz Algılanmıyor
**Çözüm:**
1. Işığı kontrol edin (yeterli aydınlatma)
2. Kameraya daha yakın durun
3. Çözünürlüğü XGA'ya ayarlayın
4. Yüzünüzü doğrudan kameraya dönün

## 💡 İpuçları

1. ✨ **İlk kullanımda** mutlaka "Optimize Et" butonuna basın
2. 🌞 **Aydınlatma önemli** - Yüz analizi için iyi ışık şart
3. 📏 **Mesafe:** 50cm-2m arası ideal
4. 🎯 **Açı:** Yüzünüzü doğrudan kameraya dönün
5. ⏱️ **Bekleme:** Ayar değişikliğinden sonra 2-3 saniye bekleyin
6. 🔄 **Yenileme:** Sorun olursa "Mevcut Ayarları Göster" ile kontrol edin

## 📊 Performans Beklentileri

| Çözünürlük | FPS | Ağ Bandı | Analiz Kalitesi |
|------------|-----|----------|-----------------|
| UXGA | ~5 | Yüksek | Mükemmel |
| SXGA | ~8 | Yüksek | Çok İyi |
| **XGA** ⭐ | **~15** | **Orta** | **Çok İyi** |
| SVGA | ~20 | Orta | İyi |
| VGA | ~30 | Düşük | Yeterli |

## 🆘 Destek

Sorun mu yaşıyorsunuz?

1. **Detaylı Kılavuz:** `ESP_CAMERA_SETTINGS.md` dosyasını okuyun
2. **Log Kontrol:** Tarayıcı Console'unu açın (F12)
3. **Ayarları Kontrol:** "Mevcut Ayarları Göster" butonunu kullanın
4. **Sıfırlama:** ESP32'yi yeniden başlatın

## 📖 İlgili Dokümanlar

- 📄 **Detaylı Ayarlar:** `ESP_CAMERA_SETTINGS.md`
- 📄 **API Referansı:** `API_REFERENCE.md`
- 📄 **Proje Genel:** `README.md`

---

**Hazır!** Artık ESP32-CAM ile duygu analizi yapmaya hazırsınız! 🎉
