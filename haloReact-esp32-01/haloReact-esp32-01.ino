/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-button-led
 */

#define BUTTON_PIN  21 // ESP32 pin GPIO21, which connected to button
#define LED_PIN_RED 19 // ESP32 pin GPIO19, which connected to led red
#define LED_PIN_YELLOW 18 // ESP32 pin GPIO18, which connected to led yello
#define BUZZ_PIN 5 // ESP32 pin GPIO5, which connected to the buzzer

// variables will change:
int button_state = 0;   // variable for reading the button status

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // initialize the LED pin as an output:
  pinMode(LED_PIN_RED, OUTPUT);
  pinMode(LED_PIN_YELLOW, OUTPUT);

  // initialize the button pin as an pull-up input:
  // the pull-up input pin will be HIGH when the button is open and LOW when the button is pressed.
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {  
  // put your main code here, to run repeatedly:
  Serial.println("Hello World!");
  delay(500);

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

}
