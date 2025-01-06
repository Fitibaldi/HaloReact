#include <WiFi.h>
#include <PubSubClient.h>
#include <FastLED.h>


/* ToBe PROD
const char* ssid     = "HaloReact";
const char* password = "HaloReact1122";
*/

// Test Wifi
const char* ssid = "Ognianovi.Guest";
const char* password = "Ognianovi1234";

// MQTT broker details
const char* mqtt_server = "192.168.0.212";
const int mqtt_port = 1883;

// MQTT topics
const char* STATUS_TOPIC = "pod_status";
const char* ACTION_TOPIC = "pod_action";

// MQTT Client
WiFiClient espClient;
PubSubClient client(espClient);

// Unique ESP32 identifier
uint64_t chipId = ESP.getEfuseMac(); // Get the 64-bit MAC address
String unique_id = "ESP32_" + String((uint16_t)(chipId >> 32), HEX) + String((uint32_t)chipId, HEX);


// Define pins
#define BUTTON_PIN 21      // ESP32 pin GPIO21, which connected to button
#define BUZZ_PIN 5         // ESP32 pin GPIO5, which connected to the buzzer
#define LED_PIN_RGB 18     // ESP32 pin GPIO18, which connected to the RGB LED
#define NUM_LEDS 12        // Number of LEDs
#define PIEZO_PIN 36       // ESP32 ADC pin on VP
const int piezo_threshold = 40;

// Define the array of leds
CRGB leds[NUM_LEDS];

int last_piezo_state = 0;
int last_button_state = 0;
String current_color_hex = "#000000";

void setup() {
  delay(2000);  // Wait 2 seconds before starting serial communication

  Serial.begin(115200);

  // initialize the button pin as an pull-up input:
  // the pull-up input pin will be HIGH when the button is open and LOW when the button is pressed.
  pinMode(BUTTON_PIN, INPUT_PULLUP); 

  pinMode(PIEZO_PIN, INPUT); // Configure the piezo pin as input

  // Setup The LED
  FastLED.addLeds<NEOPIXEL, LED_PIN_RGB>(leds, NUM_LEDS);  // GRB ordering is assumed
  FastLED.setBrightness(30);

  setup_wifi();

  unique_id.toUpperCase();
  Serial.print("Unique ID: ");
  Serial.println(unique_id.c_str());

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Ensure the client is connected
  reconnect();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int piezo_reading = analogRead(PIEZO_PIN);
  int piezo_state = (piezo_reading > piezo_threshold) ? 1 : 0;
  if (piezo_reading > 0) {
    Serial.print("Piezo reading: ");
    Serial.print(piezo_reading);
    Serial.print(" Piezo state: ");
    Serial.println(piezo_state);
  }

  // read the state of the button value:
  int button_state = digitalRead(BUTTON_PIN);
  if (button_state != last_button_state || piezo_state != last_piezo_state) {
    // Publish the current state if there is a change in the button
    String stat = "aaa";
    if (button_state != last_button_state) {
      stat = (button_state == HIGH ? "HIGH" : "LOW");
    } else {
      stat = (piezo_state == 1 ? "HIGH" : "LOW");
    }
    last_piezo_state = piezo_state;
    last_button_state = button_state;
    String status_to_publish = "STAT|" + unique_id + "|" + 
      stat + "|" + 
      current_color_hex;
    Serial.println(status_to_publish);
    client.publish(STATUS_TOPIC, status_to_publish.c_str());
  }

  delay(50);

}

void callback(char* topic, byte* message, unsigned int length) {
  String received_message = "";
  for (int i = 0; i < length; i++) {
    received_message += (char)message[i];
  }

  Serial.print("Message received on topic: ");
  Serial.print(topic);
  Serial.print("\tMessage: ");
  Serial.println(received_message);

  // Process the message from the ACTION_TOPIC
  if (String(topic) == ACTION_TOPIC) {
    // Parse the message
    int sep1 = received_message.indexOf('|');
    int sep2 = received_message.indexOf('|', sep1 + 1);
    int sep3 = received_message.indexOf('|', sep2 + 1);

    if (sep1 == -1 || sep2 == -1 || sep3 == -1) {
      Serial.println("Invalid message format.");
      return;
    }

    String command_type = received_message.substring(0, sep1);
    String pod_id = received_message.substring(sep1 + 1, sep2);
    String color_hex = received_message.substring(sep2 + 1, sep3);
    String function_name = received_message.substring(sep3 + 1);

    // Log if command type is not "NSTAT"
    if (command_type != "NSTAT") {
      Serial.println("Non-critical command received, logging only.");
      return;
    }

    // Check if the pod ID matches this ESP32's unique ID
    if (pod_id != unique_id) {
      Serial.println("Pod ID does not match, ignoring command.");
      return;
    }

    // Update LED color
    current_color_hex = color_hex;
    CRGB color = hexToCRGB(color_hex);
    lightRGB(color);
    Serial.print("Updated LED color to: ");
    Serial.println(color_hex);

    // Call the specified function
    playSound(function_name);
  }
}

// Connect to WiFi
void setup_wifi() {
  delay(100);
  Serial.print("Trying to connect to ");
  Serial.println(ssid);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Reconnect to the MQTT broker if disconnected
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(unique_id.c_str())) {
      Serial.println("Connected to MQTT broker.");
      // Publish unique identifier to pod_status
      client.publish(STATUS_TOPIC, ("HELLO|" + unique_id).c_str());
      // Subscribe to pod_action topic
      client.subscribe(ACTION_TOPIC);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 5 seconds.");
      delay(5000);
    }
  }
}

void lightRGB(CRGB color, int brightness) {
  FastLED.setBrightness(brightness);
  lightRGB(color);
}

void lightRGB(CRGB color) {
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = color;
    }
    FastLED.show();
}

// Function to convert HEX color to CRGB
CRGB hexToCRGB(String hex) {
  if (hex.startsWith("#")) hex = hex.substring(1); // Remove '#' if present
  long number = strtol(hex.c_str(), NULL, 16);
  return CRGB((number >> 16) & 0xFF, (number >> 8) & 0xFF, number & 0xFF);
}

void playSound(String function_name) {
  if (function_name == "playStartSignal") {
    playStartSignal();
  } else if (function_name == "playEndSignal") {
    playEndSignal();
  } else if (function_name == "playAsteriskSound") {
    playAsteriskSound();
  } else if (function_name == "playCalendarReminder") {
    playCalendarReminder();
  } else if (function_name == "playDeviceConnect") {
    playDeviceConnect();
  } else if (function_name == "playMessageNudge") {
    playMessageNudge();
  } else if (function_name == "playDeviceDisconnect") {
    playDeviceDisconnect();
  } else if (function_name == "playGoalSignal") {
    playGoalSignal();
  } else if (function_name == "playMessageNudge") {
    playMessageNudge();
  } else {
    Serial.println("Unknown function, no action taken.");
  }
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
