# HaloReact: DIY Interactive Light Pods

## Project Overview
HaloReact is a DIY project designed to create interactive light pods for training, gaming, and entertainment. Inspired by commercial products like BlazePods, HaloReact leverages ESP32 microcontrollers, a Raspberry Pi (or Orange Pi) server, and modern networking protocols to deliver a responsive and scalable system. This README provides detailed instructions for building and customizing your own HaloReact system.

---

## Features
- **Multicolor LEDs**: RGB LED functionality for vibrant and dynamic lighting effects.
- **Impact Detection**: Sensors detect punches, taps, or movements on the pods.
- **Mesh Networking**: ESP32 devices communicate seamlessly via a mesh network.
- **Server Integration**: Central server hosted on Raspberry Pi or Orange Pi with built-in MQTT broker.
- **Standalone Operation**: No external Wi-Fi router required.
- **Rechargeable Design**: Pods are equipped with rechargeable batteries and stackable charging connectors.
- **Sound Indication**: Pods are soundy to easily identify their location or understand the commands

---

## Hardware Requirements

### Core Components
1. **ESP32 Microcontroller** (one per pod)
2. **Raspberry Pi or Orange Pi** (for server functionality)
3. **RGB LEDs** (e.g., WS2812B or similar)
4. **Sensors**:
   - Accelerometer (e.g., MPU6050) for impact detection
   - Optional: Capacitive touch sensor or force-sensitive resistor (piezo)
5. **Rechargeable Battery** (e.g., LiPo or 18650 cells)
6. **Battery Management Module** (e.g., TP4056 for charging)
7. **Buzzer**

### Optional Components
- Piezoelectric sensors for alternative impact detection
- Enclosure materials (e.g., 3D-printed cases, transparent tops)
- Magnetic connectors for stackable charging

---

## Software Requirements

### Server Side
- **Operating System**: Raspberry Pi OS or compatible Linux distro for Orange Pi
- **Software**:
  - Python 3
  - MQTT Broker (e.g., Mosquitto)
  - Flask or Django (for web-based control interface)

### Pod Firmware
- **ESP-IDF** or **Arduino Framework** for programming ESP32
- Libraries:
  - `PubSubClient` for MQTT
  - `Adafruit_NeoPixel` for LED control
  - `Wire` for I2C communication with sensors

---

## System Architecture
1. **Wi-Fi Router Mode**:
   - Raspberry Pi or Orange Pi acts as a Wi-Fi hotspot.
   - Pods connect to the server via MQTT.
2. **Mesh Networking**:
   - ESP32 pods communicate with each other using ESP-Mesh.
   - Server manages coordination and control.

---

## Getting Started

### Step 1: Set Up the Server
   ```TBA


### Step 2: Program the Pods
1. Write firmware for the ESP32 using Arduino IDE or PlatformIO.
2. Connect the pod to the server:
3. Test sensor and LED functionality.

### Step 3: Build the Pods
1. Assemble the hardware:
   - Purchase a PCB
   - Mount the ESP32, battery, and sensors in the enclosure.
   - Wire the RGB LEDs and sensor to the ESP32.
2. Design the enclosure:
   - Use a transparent top for LED visibility.
   - Ensure charging contacts align for stackable charging.

---

## Usage
- Connect your mobile phone to the server's Wi-Fi hotspot.
- Open the control interface in your browser (e.g., `http://192.168.4.1`).
- Configure pod settings, start training programs, or play games.

---

## Future Enhancements
- **Mobile App**: Create a dedicated app for better user interaction.
- **Bluetooth Integration**: Add BLE for smartphone-to-pod direct communication.
- **Custom Sensors**: Experiment with alternative impact detection technologies.
- **Advanced Enclosures**: Optimize for durability and aesthetics.

---

## License
This project is open-source and distributed under the MIT License. Contributions and modifications are welcome.

---

## Acknowledgments
- Inspired by BlazePods and similar interactive systems.
- Special thanks to the open-source community for providing tools and libraries.
