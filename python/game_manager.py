import paho.mqtt.client as mqtt
import time
import random
from threading import Timer
from threading import Lock
import json
import os

# MQTT broker details
BROKER = "localhost"  # Change to your broker's IP if not local
PORT = 1883

# Topics
STATUS_TOPIC = "pod_status"
ACTION_TOPIC = "pod_action"

# Game State
nodes = []
game_timer_start = None
game_timer_end = None
active_nodes = set()
game_name = None
current_blinking_pod = None
muted = None

result_lock = Lock()
data_file = "static/game_statistics.json"

# Initialize the file if it doesn't exist
if not os.path.exists(data_file):
    with open(data_file, "w") as file:
        json.dump({}, file)


# Algorithm function
def determine_action(status_message):
    global game_timer_start, game_timer_end, active_nodes, current_blinking_pod, muted

    parts = status_message.split('|')
    command = parts[0]

    if command == "HELLO":
        return add_node(parts[1])
        
    elif command == "START" and parts[1] == "OUTRUN":
        muted = parts[2]
        return start_game_OUTRUN()
        
    elif command == "STAT" and game_name == "OUTRUN":
        print("In game action")
        node_id = parts[1]
        # Check if ButtonStatus is "HIGH"
        if parts[2] == "HIGH":
            # Turn off the pod and record time
            active_nodes.discard(node_id)
            action = f"NSTAT|{node_id}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}"

            if len(active_nodes) + 1 == len(nodes):  # First node clicked
                game_timer_start = time.time()
                print("Timer started!")
            elif not active_nodes:  # Last node clicked
                game_timer_end = time.time()
                duration = game_timer_end - game_timer_start
                print(f"Game finished in {duration:.2f} seconds!")
                action += f"\nENDGAME|OUTRUN|{duration:.2f} seconds!"
                save_game_statistics("OUTRUN", duration)
            
            return action
        return ""

    elif command == "START" and parts[1] == "RANDOM":
        muted = parts[2]
        return start_game_RANDOM()

    elif command == "STOP" and parts[1] == "RANDOM":
        return stop_game_RANDOM()

    elif command == "STAT" and game_name == 'RANDOM':
        node_id = parts[1]
        if parts[2] == "HIGH" and node_id == current_blinking_pod:
            # Turn off the current blinking pod and select a new one
            current_blinking_pod = random.choice([n["id"] for n in nodes if n["id"] != node_id])
            return f"NSTAT|{node_id}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}\nNSTAT|{current_blinking_pod}|#00FF00|{'playStartSignal' if muted != 'MUTED' else 'NONE'}"
        return ""     
        
    elif command == "STAT":
        # Check if ButtonStatus is "HIGH"
        if parts[2] == "HIGH":
            # If ButtonStatus is HIGH, set the new color to "Red" and BuzzMelody to "playDeviceDisconnect"
            new_color = "#500000"
            buzz_melody = "playDeviceDisconnect" if muted != 'MUTED' else "NONE"
        else:
            # If ButtonStatus is not "HIGH", retain current color and set BuzzMelody to "noAction"
            new_color = "#005000"
            buzz_melody = "playGoalSignal" if muted != 'MUTED' else "NONE"
        # Return the formatted message
        return f"NSTAT|{parts[1]}|{new_color}|{buzz_melody}"
        
    return f"ERR|unknown exception for message {status_message}"

# Function to start a game
def start_game_OUTRUN():
    global active_nodes, game_name, muted
    active_nodes = {node["id"] for node in nodes}
    
    game_name = "OUTRUN"
    
    message = ""
    for i, node in enumerate(nodes):
        color = f"#{i:02x}{255 - i:02x}{i * 2:02x}"  # Generate a unique HEX color
        message += f"NSTAT|{node['id']}|{color}|{'playStartSignal' if muted != 'MUTED' else 'NONE'}\n"
        
    message += f":: {game_name} STARTED ::"
    return message.strip()

# Function to handle the start of the Randomize Me! game
def start_game_RANDOM():
    global current_blinking_pod, game_name, game_timer_start, muted
    
    game_name = 'RANDOM'
    game_timer_start = time.time()
    
    current_blinking_pod = random.choice(nodes)["id"]  # Pick a random node
    return f"NSTAT|{current_blinking_pod}|#00FF00|{'playStartSignal' if muted != 'MUTED' else 'NONE'}"

# Function to handle the stop of the Randomize Me! game
def stop_game_RANDOM():
    global current_blinking_pod, game_name, game_timer_start, game_timer_end, muted
    
    game_name = None
    
    game_timer_end = time.time()
    duration = game_timer_end - game_timer_start
    print(f"Game finished in {duration:.2f} seconds!")
    
    current_blinking_pod = None
    save_game_statistics("RANDOM", duration)
    return f"\nENDGAME|RANDOM|{duration:.2f} seconds!\n".join([f"NSTAT|{node['id']}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}" for node in nodes])

# Function to add a new node dynamically
def add_node(node_id):
    # Adds a new node to the nodes list if it doesn't already exist.
    for node in nodes:
        if node["id"] == node_id:
            return f"ERR|Node {node_id} already exists."
            
    nodes.append({"id": node_id, "status": "active"})
    print(f"Added new node: {node_id}")
    return f"HELLO|{node_id}|DON'T PANIC"

def save_game_statistics(game_name, time_played):
    """Save game statistics to the JSON file."""
    with result_lock:
        try:
            # Load existing data
            with open(data_file, "r") as file:
                data = json.load(file)
            
            # Add new entry for the game
            if game_name in data:
                data[game_name].append(time_played)
            else:
                data[game_name] = [time_played]
            
            # Write updated data back to the file
            with open(data_file, "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving game statistics: {e}")

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    action = determine_action(msg.payload.decode())
    for row in action.split("\n"):
        if row.strip():
            client.publish(ACTION_TOPIC, row)
            print(f"Published action: {row}")

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(STATUS_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

# Main MQTT setup
def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
