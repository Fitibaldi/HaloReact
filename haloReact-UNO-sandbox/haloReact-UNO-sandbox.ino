#include <FastLED.h>
#include "HaloReactLib.h"

// Define pins
#define BUTTON_PIN  4
#define LED_PIN_RGB 2
#define PIEZO_PIN A1 
#define BUZZ_PIN 13
#define NUM_LEDS 12 

// variables will change:
int button_state = 0;   // variable for reading the button status

const int threshold = 40;

// Define the array of leds
CRGB leds[NUM_LEDS];

void setup() {
  /*
  * Normal pin initialization
  */
  Serial.begin(9600);

  // initialize the button pin as an pull-up input:
  // the pull-up input pin will be HIGH when the button is open and LOW when the button is pressed.
  pinMode(BUTTON_PIN, INPUT);
  
  FastLED.addLeds<NEOPIXEL, LED_PIN_RGB>(leds, NUM_LEDS);  // GRB ordering is assumed
  FastLED.setBrightness(30);
}

void loop() {
  // read the state of the button value:
  int val = analogRead(PIEZO_PIN);
  Serial.print("Piezo: ");
  Serial.println(val);
  button_state = digitalRead(BUTTON_PIN);
  Serial.print("Button state: ");
  Serial.println(button_state);

  // control LED according to the state of button
  if (button_state == HIGH || val >= threshold)  {      // if button is pressed
    lightRGB(CRGB::White, 100);
    
    playDeviceConnect();
    delay(1000);
    playDeviceDisconnect();
    delay(1000);

    Serial.println("Button Pressed");
  } else {                          // otherwise, button is not pressing
    lightRGB(CRGB::Orange, 20);
    Serial.println("Button De-Pressed");
  }

  delay(500);

}

void lightRGB(CRGB color, int brightness) {
  FastLED.setBrightness(brightness);
  lightRGB(color);
}

void lightRGB (CRGB color) {
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = color;
    }
    FastLED.show();
}

// Short tone for "Start Signal" (e.g., whistle-like)
void playStartSignal() {
  for (int i = 0; i < 3; i++) {
    tone(BUZZ_PIN, 800, 80);  // Lower tone
    delay(100);
    tone(BUZZ_PIN, 1000, 80); // Middle tone
    delay(100);
    tone(BUZZ_PIN, 1200, 80); // Higher tone
    delay(100);
  }
  noTone(BUZZ_PIN);
}

// Motivational tone for "Goal Signal" (e.g., celebratory chirp)
void playGoalSignal() {
  tone(BUZZ_PIN, 1200, 100); // High pitch
  delay(50);
  tone(BUZZ_PIN, 800, 100);  // Low pitch
  delay(50);
  tone(BUZZ_PIN, 1000, 200); // Middle pitch for celebration
  delay(200);
  noTone(BUZZ_PIN);
}

// Signal for "End of Activity" (e.g., descending tone)
void playEndSignal() {
  for (int i = 0; i < 3; i++) {
    tone(BUZZ_PIN, 1200 - (i * 200), 100); // Gradually lower pitch
    delay(150);
    tone(BUZZ_PIN, 800 + (i * 100), 100); // Alternate harmonic pitch
    delay(150);
  }
  noTone(BUZZ_PIN);
}


// Function to play the Windows "Asterisk" sound
void playAsteriskSound() {
  tone(BUZZ_PIN, 880, 100);  // A5 (880 Hz) for 100ms
  delay(120);                // Short pause
  tone(BUZZ_PIN, 1047, 150); // C6 (1047 Hz) for 150ms
  noTone(BUZZ_PIN);
}

// Function to play the Windows "Calendar Reminder" sound
void playCalendarReminder() {
  tone(BUZZ_PIN, 1047, 150); // C6 (1047 Hz) for 150ms
  delay(200);                // Short pause
  tone(BUZZ_PIN, 880, 150);  // A5 (880 Hz) for 150ms
  delay(200);                // Short pause
  tone(BUZZ_PIN, 698, 200);  // F5 (698 Hz) for 200ms
}

// Function to play the Windows "Device Connect" sound
void playDeviceConnect() {
  tone(BUZZ_PIN, 784, 150);  // G5 (784 Hz) for 150ms
  delay(200);                // Short pause
  tone(BUZZ_PIN, 988, 200);  // B5 (988 Hz) for 200ms
}

// Function to play the Windows "Device Disconnect" sound
void playDeviceDisconnect() {
  tone(BUZZ_PIN, 988, 150);  // B5 (988 Hz) for 150ms
  delay(200);                // Short pause
  tone(BUZZ_PIN, 784, 200);  // G5 (784 Hz) for 200ms
}

// Function to play the Windows "Message Nudge" sound
void playMessageNudge() {
  tone(BUZZ_PIN, 880, 100);  // A5 (880 Hz) for 100ms
  delay(100);                // Short pause
  tone(BUZZ_PIN, 988, 100);  // B5 (988 Hz) for 100ms
}