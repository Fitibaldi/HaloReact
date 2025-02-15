#include <WiFi.h>
#include <ESPAsyncWebServer.h>


const char* ssid     = "HaloReact";
const char* password = "HaloReact1122";

#define LED_PIN 48  // Change this if using a different pin or built-in LED

AsyncWebServer server(80);

void setup() {
  Serial.begin(9600);
  Serial.println("Initialization");

  delay(1000); // wait 1s before initialization

  pinMode(LED_PIN, OUTPUT);  // Set LED pin as output

  digitalWrite(LED_PIN, HIGH);  // Turn the LED on
  delay(100);                  // Wait for 0.1 second
  digitalWrite(LED_PIN, LOW);   // Turn the LED off
  delay(100);                 // Wait for 0.1 second
  digitalWrite(LED_PIN, HIGH);  // Turn the LED on
  delay(1000);                // Wait for 1 second
  digitalWrite(LED_PIN, LOW); // Turn the LED off

  // Setup AP
  Serial.println("Setting AP (Access Point)… ");
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  // Redirect to Flask server when clients connect
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/html",
        "<html><head><meta http-equiv='refresh' content='0;url=http://192.168.4.200:5000'></head>"
        "<body><p>Redirecting...</p></body></html>");
  });

    // Start web server
    server.begin();
}

void loop() {
  digitalWrite(LED_PIN, HIGH);  // Turn the LED on
  delay(1000);                  // Wait for 1 second
  digitalWrite(LED_PIN, LOW);   // Turn the LED off
  delay(1000);                  // Wait for 1 second
  Serial.print(".");
}