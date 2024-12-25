import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "localhost"  # Change to your broker's IP if not local
PORT = 1883

# Topics
STATUS_TOPIC = "pod_status"
ACTION_TOPIC = "pod_action"

# Array of nodes
nodes = []

# Algorithm function
def determine_action(status_message):
    # Split the status_message into parts
    # The max possible parts are: Command, NodeID, ButtonStatus, and CurrColor
    parts = status_message.split('|')
    command = parts[0]

    # Check the Command
    if command == "HELLO":
        # Add the node to the list of players and return HELLO
        return add_node(parts[1])
        
    elif command == "START":
        message = start_game(parts[1])
        return message + f"\n:: {parts[1]} STARTED ::"
        
    elif command == "STAT":
        # Check if ButtonStatus is "HIGH"
        if parts[2] == "HIGH":
            # If ButtonStatus is HIGH, set the new color to "Red" and BuzzMelody to "playDeviceDisconnect"
            new_color = "#500000"
            buzz_melody = "playDeviceDisconnect"
        else:
            # If ButtonStatus is not "HIGH", retain current color and set BuzzMelody to "noAction"
            new_color = "#005000"
            buzz_melody = "playGoalSignal"
        # Return the formatted message
        return f"NSTAT|{parts[1]}|{new_color}|{buzz_melody}"
        
    return f"ERR|unknown exception for message {status_message}"

# Function to start a game
# Later this function will determine the game as well
def start_game(game_name):
    message = ""
    for node in nodes:
        print(f"NSTAT|{node['id']}|#100000|playDeviceDisconnect")
        message += f"\nNSTAT|{node['id']}|#100000|playDeviceDisconnect"
        
    return message.strip() # Remobing the trailing new Line

# Function to add a new node dynamically
def add_node(node_id):
    # Adds a new node to the nodes list if it doesn't already exist.
    for node in nodes:
        if node["id"] == node_id:
            return f"ERR|Node {node_id} already exists."
    
    nodes.append({"id": node_id, "status": "active"})
    print(f"Added new node: {node_id}")
    return f"HELLO|{node_id}|DON'T PANIC"

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    # Process the message and determine the action
    action = determine_action(msg.payload.decode())
    # Loop over each row in the returned message and publish it
    for row in action.split("\n"):
        # Publish the action to the ACTION_TOPIC
        client.publish(ACTION_TOPIC, row)
        print(f"Published action: {row}")

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
