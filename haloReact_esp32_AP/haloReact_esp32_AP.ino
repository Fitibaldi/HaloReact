#include <WiFi.h>

const char* ssid     = "HaloReact";
const char* password = "HaloReact1122";

#define LED_PIN 8  // Change this if using a different pin or built-in LED

void setup() {
  pinMode(LED_PIN, OUTPUT);  // Set LED pin as output
  
  Serial.begin(9600);

  // Setup AP
  Serial.println("Setting AP (Access Point)… ");
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);  // Turn the LED on
  delay(1000);                  // Wait for 1 second
  digitalWrite(LED_PIN, LOW);   // Turn the LED off
  delay(1000);                  // Wait for 1 second
}