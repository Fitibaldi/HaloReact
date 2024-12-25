#include <WiFi.h>
#include <PubSubClient.h>

/* ToBe PROD
const char* ssid     = "HaloReact";
const char* password = "HaloReact1122";
*/

// Test Wifi
const char* ssid     = "Ognianov.450";
const char* password = "Start2018";

// MQTT Client
WiFiClient espClient;
PubSubClient mqttClient(espClient);

const char* mqttTopic = "pods/topic";

// Define pins
#define BUTTON_PIN  21 // ESP32 pin GPIO21, which connected to button
#define LED_PIN_RED 19 // ESP32 pin GPIO19, which connected to led red
#define LED_PIN_YELLOW 18 // ESP32 pin GPIO18, which connected to led yello
#define BUZZ_PIN 5 // ESP32 pin GPIO5, which connected to the buzzer

// variables will change:
int button_state = 0;   // variable for reading the button status

void setup() {
  /*
  * Normal pin initialization
  */
  Serial.begin(9600);

  // initialize the LED pin as an output:
  pinMode(LED_PIN_RED, OUTPUT);
  pinMode(LED_PIN_YELLOW, OUTPUT);

  // initialize the button pin as an pull-up input:
  // the pull-up input pin will be HIGH when the button is open and LOW when the button is pressed.
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  /*
  * WiFi initializationi
  * if cannot connect to the WiFi, then it becomes AP. that means that this is the first pod started
  */
  WiFi.begin(ssid, password);
  if (WiFi.status() == WL_CONNECTED) { //attempt 1
    pod_role = "client";
  } else {
    delay (1000);
  }
  if (WiFi.status() == WL_CONNECTED) { //attempt 2
    pod_role = "client";
  } else {
    pod_role = "server";
  }

  Serial.print("Role: ");
  Serial.println(pod_role);
  if (pod_role == "server") {
    // Setup AP
    Serial.print("Setting AP (Access Point)… ");
    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);

    //Start MQTT broker
    mqttBroker.init(1883);
    Serial.println("MQTT Broker started");
  }

  // Configure MQTT Client
  mqttClient.setServer("192.168.4.1", 1883); // Connect to local broker
  mqttClient.setCallback(callback);

  // Connect MQTT Client to Broker
  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT broker...");
    if (mqttClient.connect("ESP32Client")) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed to connect, rc=");
      Serial.print(mqttClient.state());
      delay(2000);
    }
  }

  // Subscribe to a topic
  mqttClient.subscribe(mqttTopic);
}

void loop() {
  // read the state of the button value:
  button_state = digitalRead(BUTTON_PIN);
  Serial.print("Button state: ");
  Serial.println(button_state);

  // control LED according to the state of button
  if (button_state == HIGH)  {      // if button is pressed
    digitalWrite(LED_PIN_RED, HIGH); // turn on LED
    digitalWrite(LED_PIN_YELLOW, HIGH); // turn on LED
    Serial.println("Button Pressed");
  } else {                          // otherwise, button is not pressing
    digitalWrite(LED_PIN_RED, LOW);  // turn off LED
    digitalWrite(LED_PIN_YELLOW, LOW);  // turn off LED
  }

  mqttClient.loop();

  // Publish a message periodically
  static unsigned long lastMessage = 0;
  if (millis() - lastMessage > 5000) {
    lastMessage = millis();
    mqttClient.publish(mqttTopic, "Hello from ESP!");
    Serial.println("Message published");
  }

}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}
