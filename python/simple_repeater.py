import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "localhost"  # Change to your broker's IP if not local
PORT = 1883

# Topics
STATUS_TOPIC = "pod_status"
ACTION_TOPIC = "pod_action"

# Algorithm function
def determine_action(status_message):
    # Split the status_message into 3 parts: NodeID, ButtonStatus, and CurrColor
    node_id, button_status, curr_color = status_message.split('|')

    # Check if ButtonStatus is "HIGH"
    if button_status == "HIGH":
        # If ButtonStatus is HIGH, set the new color to "Black" and BuzzMelody to "playDeviceDisconnect"
        new_color = "Black"
        buzz_melody = "playDeviceDisconnect"
    else:
        # If ButtonStatus is not "HIGH", retain current color and set BuzzMelody to "noAction"
        new_color = curr_color
        buzz_melody = "noAction"

    # Return the formatted message
    return f"{node_id}|{new_color}|{buzz_melody}"

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    # Process the message and determine the action
    action = determine_action(msg.payload.decode())
    # Publish the action to the ACTION_TOPIC
    client.publish(ACTION_TOPIC, action)
    print(f"Published action: {action}")

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe to the STATUS_TOPIC
        client.subscribe(STATUS_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

# Main MQTT setup
def main():
    # Initialize the MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(BROKER, PORT, 60)

    # Loop forever, processing incoming messages
    client.loop_forever()

if __name__ == "__main__":
    main()
