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
2. **Raspberry Pi Zero 2W or Orange Pi Zero** (for server functionality)
3. **RGB LEDs** (e.g., WS2812B or similar)
4. **Sensors**:
   - Piezoelectric sensors for alternative impact detection
5. **Rechargeable Battery** (e.g., LiPo or 18650 cells)
6. **Battery Management Module** (e.g., TP4056 for charging)
7. **Buzzer** to play sounds
8. PCB to mount everything

### Optional Components
- Optional: Accelerometer (e.g., MPU6050) for impact detection
- Optional: Capacitive touch sensor or force-sensitive resistor (piezo)
- Enclosure materials (e.g., 3D-printed cases, transparent tops)
- Magnetic connectors (pogo pins) for stackable charging

---

## Software Requirements

### Server Side
- **Operating System**: Raspberry Pi OS or compatible Linux distro for Orange Pi (Armbian)
- **Software**:
  - Python 3
  - MQTT Broker (e.g., Mosquitto)
  - Flask or Django (for web-based control interface)

### Pod Firmware
- **ESP-IDF** or **Arduino Framework** for programming ESP32
- Libraries:
  - `PubSubClient` for MQTT
  - `FastLED` for LED control
  - `WiFi` for wireless communication

---

## System Architecture
- ESP-C3 acts as a Wi-Fi hotspot.
- Raspberry Pi/Orange Pi acts as a App Server, Python game manager and MQTT broker
- Pods connect to the server via MQTT.

---

## Getting Started

### Step 1: Set Up the Server
1. Make ESP-C3 to be AP (TBA)

1.1. Configure Orange Pi Zero to connect to HaloReact Wifi network:
```bash
nmtui
```
2. Install Mosquitto:
```bash
apt install mosquitto mosquitto-client
```
2.1. Start Mosquitto:
```bash
sudo systemctl start mosquitto
```
2.2. Configure Mosquitto to listen on IP, not only on localhost:
```bash
netstat -tlnp | grep 1883
sudo nano /etc/mosquitto/mosquitto.conf
```
- Add or modify the following lines:
```bash
listener 1883
allow_anonymous true
```
- Restart the broker:
```bash
sudo systemctl restart mosquitto
```
3. Setup MQTT topics
```bash
mosquitto_sub -h localhost -t pod_status
mosquitto_sub -h localhost -t pod_action
mosquitto_pub -h localhost -t pod_status -m "HELLO|N1"
mosquitto_pub -h localhost -t pod_status -m "STAT|N1|HIGH|Red"
```
4. Install python
```bash
apt install python3 python3-pip
```
5. Create separate environment for python and activate it
```bash
python3 -m venv myenv
source myenv/bin/activate
```
6. Install Flask App Server
```bash
pip3 install flask
pip install paho-mqtt
```
7. Run the script
```bash
python3 simple_repeater.py
python3 game_manager.py
```
8. Play a fake game
```bash
mosquitto_pub -h localhost -t pod_status -m "HELLO|N1"
mosquitto_pub -h localhost -t pod_status -m "HELLO|N2"
mosquitto_pub -h localhost -t pod_status -m "START|OUTRUN"
mosquitto_pub -h localhost -t pod_status -m "STAT|N2|HIGH|#121212"
sleep 8
mosquitto_pub -h localhost -t pod_status -m "STAT|N1|HIGH|#121212"
```

#### Setting a Static IP for `wlan0` Using `nmcli`

Follow these steps to set a static IP on an existing Wi-Fi connection using `nmcli`:

1. **Find the existing connection name**:
```bash
nmcli con show
```
   
This command lists all network connections. Identify the connection associated with wlan0. For example, if the connection name is WIFI_HOME, proceed with the following steps.

2. **Modify the connection to use a static IP**:
```bash
sudo nmcli con modify WIFI_HOME ipv4.addresses 192.168.4.200/24
sudo nmcli con modify WIFI_HOME ipv4.gateway 192.168.4.1
sudo nmcli con modify WIFI_HOME ipv4.dns 192.168.4.1
sudo nmcli con modify WIFI_HOME ipv4.method manual
```
	
3. **Restart the connection to apply the changes**:
```bash
sudo nmcli con down WIFI_HOME
sudo nmcli con up WIFI_HOME
```
	
4. **Verify the IP address**:
```bash
ip addr show wlan0
```

#### Enable mDNS on Raspberry Pi
1. **Ensure Avahi is installed on the Raspberry Pi:**
```bash
sudo apt update
sudo apt install avahi-daemon -y
```

2. **Start and enable Avahi:**
```bash
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```

3. **Check if Avahi is running:**
```bash
systemctl status avahi-daemon
```

4. **Try pinging again from another computer:**
```bash
ping raspberrypi.local
```

#### Make the server to automatically start on Orange/Raspberry start
##### APP Server Configuration
1. **Create a service**:
```bash
sudo nano /etc/systemd/system/app_server.service
```
	
2. **Add the following content**:
```ini
[Unit]
Description=Flask App Server for the HaloReact Game Webpage
After=network.target

[Service]
# User=haloreact
WorkingDirectory=/home/haloreact/HaloReact
ExecStart=/home/haloreact/myenv/bin/python3 app_server.py
Restart=always
Environment=FLASK_ENV=production
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

##### Game Manager Configuration
1. **Create a service**:
```bash
sudo nano /etc/systemd/system/game_manager.service
```

2. **Add the following content**:
```ini
[Unit]
Description=Game Manager for MQTT and pods
After=network.target

[Service]
User=haloreact
WorkingDirectory=/home/haloreact/HaloReact
ExecStart=/home/haloreact/myenv/bin/python3 game_manager.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

#### Enable, Start and Status of the Services:
- **Commands**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable app_server.service
sudo systemctl enable game_manager.service
sudo systemctl start app_server.service
sudo systemctl start game_manager.service
sudo systemctl status app_server.service
sudo systemctl status game_manager.service
sudo journalctl -u app_server.service
sudo journalctl -u game_manager.service
```

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
