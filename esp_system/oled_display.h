// OLED Display Manager Header
// Manages SSD1306 OLED display for emotion visualization

#ifndef OLED_DISPLAY_H
#define OLED_DISPLAY_H

#include <Arduino.h>

// Initialize OLED display
// Returns true if successful, false otherwise
bool oled_display_init();

// Display emotion with confidence score
// emotion: emotion name in English (e.g., "happy", "sad", "angry")
// confidence: confidence score between 0.0 and 1.0
void oled_display_emotion(const char* emotion, float confidence);

// Display custom message on two lines
void oled_display_message(const char* line1, const char* line2);

// Clear the display
void oled_display_clear();

// Display "waiting for data" message
void oled_display_waiting();

// Display error message
void oled_display_error(const char* error_msg);

#endif // OLED_DISPLAY_H
