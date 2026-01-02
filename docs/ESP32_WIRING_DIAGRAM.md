# ESP32 (Deneyap) Bağlantı Şeması

## 📋 Genel Bakış

Bu projede kullanılan ESP32 tabanlı Deneyap Geliştirme Kartı, dahili kamera modülü ve harici OLED ekran ile çalışmaktadır.

---

## 🔌 Pin Bağlantı Tablosu

| Bileşen | Pin Adı | ESP32 Pin | Açıklama |
|---------|---------|-----------|----------|
| **OLED Ekran (SSD1306)** | | | I2C İletişimi |
| | SDA | D10 (GPIO21) | Seri Veri Hattı |
| | SCL | D5 (GPIO19) | Seri Clock Hattı |
| | VCC | 3.3V | Güç |
| | GND | GND | Toprak |
| **Dahili Kamera** | | | Bileşik Pin Grubunun Parçası |
| | D0 | CAMD2 | Kamera Veri Hattı |
| | D1 | CAMD3 | Kamera Veri Hattı |
| | D2 | CAMD4 | Kamera Veri Hattı |
| | D3 | CAMD5 | Kamera Veri Hattı |
| | D4 | CAMD6 | Kamera Veri Hattı |
| | D5 | CAMD7 | Kamera Veri Hattı |
| | D6 | CAMD8 | Kamera Veri Hattı |
| | D7 | CAMD9 | Kamera Veri Hattı |
| | VS | CAMC | Dikey Sync |
| | HS | CAMH | Yatay Sync |
| | PCLK | CAMA | Pixel Clock |
| | XCLK | CAMX | Referans Clock |
| **USB Bağlantı** | | | Program Yükleme ve Güç |

---

## 🎨 ASCII Bağlantı Şeması

```
┌─────────────────────────────────────────────────────────────────┐
│              ESP32 DENEYAP GELİŞTİRME KARTI                    │
│         (WiFi + Kamera + OLED Desteği Sistemi)                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   SSD1306 OLED       │         │   Dahili Kamera      │
│   128x64 I2C         │         │   (OV2640)           │
│                      │         │                      │
│  ┌────────────────┐  │         │  ┌────────────────┐  │
│  │  VCC  ─────────────3.3V    │  │ Harici Açılı   │  │
│  │  GND  ─────────────GND     │  │ Konnektör      │  │
│  │  SDA  ─────────────D10     │  │ (Dahili)       │  │
│  │  SCL  ─────────────D5      │  └────────────────┘  │
│  └────────────────┘  │         │                      │
└──────────────────────┘         └──────────────────────┘
         ▲                                   ▲
         │ I2C İletişimi                    │
         └──────────────────────────────────┘
                      │
                      │
           ┌──────────┴──────────┐
           │                     │
      ┌────────────┐        ┌────────────┐
      │  D10 (SDA) │        │  D5 (SCL)  │
      │  GPIO21    │        │  GPIO19    │
      └────────────┘        └────────────┘
           │                     │
           └─────────┬───────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    ┌─────────────────────────────────────┐
    │    ESP32 İç Devreler (SoC)         │
    │                                     │
    │  • Dual Core CPU                   │
    │  • WiFi & Bluetooth                │
    │  • 4MB Flash Memory                │
    │  • ADC, I2C, SPI, UART             │
    │  • Dahili Kamera Kontrolör         │
    │  • Kamera Interface                │
    └─────────────────────────────────────┘
           │                │
           │                │
      ┌────┴────┐      ┌────┴────┐
      │ Kamera  │      │ Antennalar
      │ Veri    │      │ (WiFi/BLE)
      │ (8-bit) │      └─────────
      └────┬────┘
           │
      ┌────┴────────────────┐
      │ OV2640 Kamera Chip  │
      │                     │
      │ • Lens Kontrolü     │
      │ • Görüntü İşleme    │
      │ • JPEG Kodlaması    │
      └─────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                     GÜÇLENDIRME ŞEMASI                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  USB-C → Power Management IC → 3.3V Regülatör                 │
│  (5V)                            ↓                             │
│                          ┌────────┴────────┐                   │
│                          │                 │                   │
│                    ESP32 Çipi         OLED Ekranı              │
│                    (3.3V)             (3.3V)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Detaylı Bağlantı Diyagramı

### 1. I2C Bağlantısı (OLED için)

```
┌─────────────────────────────────────────┐
│        SSD1306 OLED Ekran               │
│      (128x64 Monochrom Display)         │
│                                         │
│  ┌─────────┐  ┌─────────┐              │
│  │  VCC    │  │   GND   │              │
│  │ (+3.3V) │  │ (0V)    │              │
│  └────┬────┘  └────┬────┘              │
│       │            │                   │
│  ┌────┴────┐  ┌───┴─────┐             │
│  │   SDA   │  │   SCL   │             │
│  │ (Data)  │  │ (Clock) │             │
│  └────┬────┘  └────┬────┘             │
│       │            │                   │
└───────┼────────────┼───────────────────┘
        │            │
        │            │ I2C Bus
        │            │ (100 kHz - 400 kHz)
        │            │
   ┌────┴────┐  ┌───┴─────┐
   │GPIO21   │  │ GPIO19  │
   │(D10)    │  │  (D5)   │
   │   SDA   │  │  SCL    │
   └─────────┘  └─────────┘
        │            │
        └────┬───────┘
             │
        ┌────┴────────┐
        │  ESP32      │
        │  I2C Master │
        └─────────────┘
```

### 2. Kamera Bağlantısı (Dahili - Entegre)

```
ESP32 dahili kamera arayüzü:
┌─────────────────────────────────────────┐
│       OV2640 Kamera (Dahili)           │
│      8-bit Parallel Interface          │
│                                         │
│  Data Lines (8 bits):                  │
│  ┌──────────────────────┐              │
│  │ D0(GPIO5) ──┐        │              │
│  │ D1(GPIO18)──┤        │              │
│  │ D2(GPIO19)──┤        │              │
│  │ D3(GPIO21)──┤ 8-bit  │              │
│  │ D4(GPIO22)──┤ Parallel              │
│  │ D5(GPIO23)──┤ Interface             │
│  │ D6(GPIO25)──┤        │              │
│  │ D7(GPIO26)──┘        │              │
│  └──────────────────────┘              │
│                                         │
│  Control Signals:                      │
│  ┌──────────────────────┐              │
│  │ VSYNC   ─→ GPIO27    │              │
│  │ HSYNC   ─→ GPIO35    │              │
│  │ PCLK    ─→ GPIO25    │              │
│  │ XCLK    ─→ GPIO32    │              │
│  └──────────────────────┘              │
└─────────────────────────────────────────┘
         ↓
    ┌──────────┐
    │  ESP32   │
    │  Camera  │
    │ Controller
    │          │
    │ WiFi modul via
    │ kameranın veri   
    │ stream işleme    
    └──────────┘
```

---

## ⚡ Güç Yönetimi

```
USB Type-C
    │
    ↓
┌────────────────┐
│ Power Mgmt IC  │  (Analog Devices / TPS63000)
└────────────────┘
    │
    ├─────────────→ 3.3V Regülatör
    │                    │
    │                    └─────┬──────────────┐
    │                         │              │
    ↓                     ┌────┴────┐    ┌────┴────┐
  GND ────────────────→  │ ESP32    │    │  OLED   │
                         │  (3.3V)  │    │  (3.3V) │
                         └──────────┘    └─────────┘

Akım Tüketimi:
┌──────────────────────────────┐
│ ESP32 Kamerasız    : ~80 mA  │
│ + Kamera Aktif     : ~160 mA │
│ + WiFi Streaming   : ~200 mA │
│ + OLED Display     : +5 mA   │
│ ─────────────────────────────│
│ Toplam Maks       : ~205 mA  │
└──────────────────────────────┘
```

---

## 📱 WiFi & Haberleşme

```
┌─────────────────────────────────┐
│    ESP32 WiFi Modülü            │
│                                 │
│  • IEEE 802.11 b/g/n            │
│  • 2.4 GHz Frekansı             │
│  • Antenna (Dahili / Harici)    │
└────────────┬────────────────────┘
             │
             ├─→ WiFi Router/Access Point
             │
             ├─→ Python Application
             │   (main.py)
             │
             └─→ WebSocket Stream
                 (Kamera yayını)
```

---

## 🛠️ Yazılım Mimarisi

```
┌─────────────────────────────────────────┐
│   Arduino Firmware (C++)                │
│   esp_system.ino                        │
└────────────────┬────────────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
    ┌───┴──┐ ┌──┴───┐ ┌──┴───┐
    │Camera│ │ OLED │ │ WiFi │
    │Module│ │Driver│ │ Stack│
    └───┬──┘ └──┬───┘ └──┬───┘
        │       │        │
        └───┬───┴────┬───┘
            │        │
    ┌───────┴─────────┴──────┐
    │  ESP32 Hardware         │
    │  (GPIO, I2C, SPI, etc)  │
    └───────────────────────────┘
            │
            ↓ HTTP/REST API
    ┌─────────────────────┐
    │  Python Backend     │
    │  (main.py)          │
    │                     │
    │ • Face Detection    │
    │ • Emotion Analysis  │
    │ • OLED Commands     │
    └─────────────────────┘
```

---

## 🔌 Bağlantı Kontrol Listesi

### Kurulumdan Önce:

- [ ] ESP32 kartı bilgisayarınıza USB kablo ile bağlı mı?
- [ ] OLED ekran 3.3V güç alıyor mu?
- [ ] SDA (D10) ve SCL (D5) kablolarının doğru pinlere bağlı olduğu doğrulandı mı?
- [ ] Hiçbir kablo gevşek veya kısa devre yapan kablo yok mu?
- [ ] OLED'in I2C adresi doğru mu (varsayılan: 0x3C)?

### Yazılım Yükleme:

1. Arduino IDE'de "Deneyap Geliştirme Kartı"ı seçin
2. "Tools > Partition Scheme" → "Huge APP" seçin
3. WiFi SSID ve şifresini `esp_system.ino`de güncelleyin
4. Kodu yükleyin
5. Seri monitörü açın (115200 baud)
6. ESP32'nin IP adresini not edin

### Test Etme:

```bash
# Python uygulamasını başlatın
python main.py

# İstendiğinde OLED URL'sini girin:
# http://<ESP32_IP>/face_mood
```

---

## 🐛 Sorun Giderme

| Sorun | Nedeni | Çözüm |
|-------|--------|-------|
| OLED görünmüyor | I2C iletişim başarısız | SDA/SCL bağlantılarını kontrol edin |
| ESP32 başlamıyor | USB bağlantı sorunu | Farklı USB kablı veya port deneyin |
| WiFi bağlanamıyor | Yanlış SSID/Şifre | Kod içindeki WiFi ayarlarını kontrol edin |
| Kamera görüntüsü yok | Kamera konnektörü gevşek | Kamera kablonun doğru takılı olduğunu kontrol edin |
| OLED hata: 0x3D adresi | Farklı I2C adresi | Koda `0x3D` adresini ekleyin |

---

## 📚 Faydalı Kaynaklar

- Deneyap Geliştirme Kartı: https://deneyapkart.org
- ESP32 Pinout: https://docs.espressif.com
- SSD1306 Veri Sayfası: https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
- OV2640 Kamera: https://github.com/espressif/esp32-camera

---

**Son Güncelleme:** 2 Ocak 2026
**Sistem:** ESP32 + OV2640 Kamera + SSD1306 OLED
