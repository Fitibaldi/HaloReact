#include <FastLED.h>

// Define pins
#define BUTTON_PIN  4
#define LED_PIN_RGB 2
#define PIEZO_PIN A1 
#define BUZZ_PIN 13
#define NUM_LEDS 12 

// variables will change:
int button_state = 0;   // variable for reading the button status

const int threshold = 10;

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
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CRGB::Red;
    }
    FastLED.show();
    Serial.println("Button Pressed");
  } else {                          // otherwise, button is not pressing
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB::Black;
  }
    FastLED.show();
    Serial.println("Button De-Pressed");
  }

  delay(500);

}
