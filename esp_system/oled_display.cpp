// OLED Display Manager for ESP32
// Displays facial emotion recognition results on SSD1306 OLED screen

#include "oled_display.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "deneyap.h"
#include "esp_log.h"

static const char *TAG = "oled_display";

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_I2C_ADDRESS 0x3C

// I2C pinleri - Deneyap Kart için
#define SDA_PIN D10
#define SCL_PIN D11

static Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
static bool display_initialized = false;

// Türkçe duygu isimleri
struct EmotionMap {
  const char* english;
  const char* turkish;
};

static const EmotionMap emotion_translations[] = {
  {"happy", "Mutlu"},
  {"sad", "Uzgun"},
  {"angry", "Kizgin"},
  {"neutral", "Notr"},
  {"surprise", "Saskin"},
  {"fear", "Korkmus"},
  {"disgust", "Tiksinmis"},
  {"unknown", "Bilinmeyen"}
};

// Initialize OLED display
bool oled_display_init() {
  if (display_initialized) {
    return true;
  }

  ESP_LOGI(TAG, "OLED ekran baslatiliyor...");
  
  // I2C başlat - Deneyap Kart için SDA=D10, SCL=D11
  Wire.begin(SDA_PIN, SCL_PIN);
  
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS)) {
    ESP_LOGE(TAG, "OLED ekran baslatilamadi!");
    return false;
  }

  display_initialized = true;
  
  // Hoş geldin mesajı
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 20);
  display.println("Deneyap");
  display.setCursor(10, 40);
  display.println("Kamera");
  display.display();
  
  ESP_LOGI(TAG, "OLED ekran basariyla baslatildi");
  delay(2000);
  
  return true;
}

// Translate emotion from English to Turkish
const char* translate_emotion(const char* emotion) {
  for (int i = 0; i < sizeof(emotion_translations) / sizeof(EmotionMap); i++) {
    if (strcmp(emotion, emotion_translations[i].english) == 0) {
      return emotion_translations[i].turkish;
    }
  }
  return "Bilinmeyen";
}

// Display emotion on OLED screen
void oled_display_emotion(const char* emotion, float confidence) {
  if (!display_initialized) {
    ESP_LOGW(TAG, "OLED ekran baslatilmamis, baslat...");
    if (!oled_display_init()) {
      return;
    }
  }

  const char* emotion_tr = translate_emotion(emotion);
  
  ESP_LOGI(TAG, "Ekranda gosteriliyor: %s (%.2f%%)", emotion_tr, confidence * 100);

  display.clearDisplay();
  
  // Başlık
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Duygu Durumu:");
  
  // Çizgi
  display.drawLine(0, 12, SCREEN_WIDTH, 12, SSD1306_WHITE);
  
  // Ana duygu - büyük font
  display.setTextSize(2);
  int emotion_len = strlen(emotion_tr);
  int x_pos = (SCREEN_WIDTH - (emotion_len * 12)) / 2;  // Ortala
  display.setCursor(x_pos, 25);
  display.println(emotion_tr);
  
  // Güven skoru
  display.setTextSize(1);
  char confidence_str[32];
  snprintf(confidence_str, sizeof(confidence_str), "Guven: %.1f%%", confidence * 100);
  int conf_len = strlen(confidence_str);
  int conf_x = (SCREEN_WIDTH - (conf_len * 6)) / 2;
  display.setCursor(conf_x, 50);
  display.println(confidence_str);
  
  // Çubuk grafik - güven seviyesi
  int bar_width = (int)(confidence * (SCREEN_WIDTH - 20));
  display.drawRect(10, 60, SCREEN_WIDTH - 20, 4, SSD1306_WHITE);
  display.fillRect(10, 60, bar_width, 4, SSD1306_WHITE);
  
  display.display();
}

// Display custom message
void oled_display_message(const char* line1, const char* line2) {
  if (!display_initialized) {
    if (!oled_display_init()) {
      return;
    }
  }

  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  
  if (line1 != NULL) {
    display.setCursor(10, 20);
    display.println(line1);
  }
  
  if (line2 != NULL) {
    display.setCursor(10, 40);
    display.println(line2);
  }
  
  display.display();
}

// Clear display
void oled_display_clear() {
  if (!display_initialized) {
    return;
  }
  
  display.clearDisplay();
  display.display();
}

// Display "waiting for data" message
void oled_display_waiting() {
  oled_display_message("Veri", "Bekleniyor");
}

// Display error message
void oled_display_error(const char* error_msg) {
  if (!display_initialized) {
    if (!oled_display_init()) {
      return;
    }
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("HATA:");
  display.setCursor(0, 15);
  display.println(error_msg);
  display.display();
}
