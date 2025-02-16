import paho.mqtt.client as mqtt
import time
import random
from threading import Timer
from threading import Lock
from collections import defaultdict
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
brighness = None

#For CHALLENGER
player_scores = defaultdict(int)  # Track taps per player
player_pods = {}  # Stores which pod is currently assigned to each player
# Define player colors (example colors in HEX)
PLAYER_COLORS = {
    1: "#FF0000",  # Red
    2: "#0000FF",  # Blue
    3: "#00FF00",  # Green
    4: "#FFFF00"   # Yellow
}

result_lock = Lock()
data_file = "static/game_statistics.json"

# Initialize the file if it doesn't exist
if not os.path.exists(data_file):
    with open(data_file, "w") as file:
        json.dump({}, file)


# Algorithm function
def determine_action(status_message):
    global game_timer_start, game_timer_end, active_nodes, current_blinking_pod, muted, brighness, player_scores, player_pods

    parts = status_message.split('|')
    command = parts[0]

    if command == "HELLO":
        return add_node(parts[1])
        
    elif command == "START" and parts[1] == "OUTRUN":
        muted = parts[2]
        brighness = parts[3]
        return start_game_OUTRUN()
        
    elif command == "STAT" and game_name == "OUTRUN":
        print("In game action")
        node_id = parts[1]
        # Check if ButtonStatus is "HIGH"
        if parts[2] == "HIGH":
            # Turn off the pod and record time
            active_nodes.discard(node_id)
            action = f"NSTAT|{node_id}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}|{brighness}"

            if len(active_nodes) + 1 == len(nodes):  # First node clicked
                game_timer_start = time.time()
                print("Timer started!")
            if not active_nodes:  # Last node clicked
                game_timer_end = time.time()
                duration = game_timer_end - game_timer_start
                print(f"Game finished in {duration:.2f} seconds!")
                action += f"\nENDGAME|OUTRUN|{duration:.2f} seconds!"
                save_game_statistics("OUTRUN", duration)
            
            return action
        return ""

    elif command == "START" and parts[1] == "RANDOM":
        muted = parts[2]
        brighness = parts[3]
        return start_game_RANDOM()

    elif command == "STOP" and parts[1] == "RANDOM":
        return stop_game_RANDOM()

    elif command == "STAT" and game_name == 'RANDOM':
        node_id = parts[1]
        if parts[2] == "HIGH" and node_id == current_blinking_pod:
            # Turn off the current blinking pod and select a new one
            valid_nodes = [n["id"] for n in nodes if n["id"] != node_id]
            
            if valid_nodes:
                current_blinking_pod = random.choice(valid_nodes)
            else:
                current_blinking_pod = node_id
            
            color = get_random_color()  # Generate a unique HEX color
            return (
                f"NSTAT|{node_id}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}|{brighness}\n"
                f"NSTAT|{current_blinking_pod}|{color}|{'playStartSignal' if muted != 'MUTED' else 'NONE'}|{brighness}"
)

        return ""
        
    elif command == "START" and parts[1] == "CHALLENGER":
        muted = parts[2]
        brighness = parts[3]
        return start_game_CHALLENGER(int(parts[4]))

    elif command == "STOP" and parts[1] == "CHALLENGER":
        return stop_game_CHALLENGER()

    elif command == "STAT" and game_name == 'CHALLENGER':
        node_id = parts[1]
        
        if parts[2] == "HIGH":
            # Find which player owns the tapped pod
            player_id = next((p_id for p_id, pod_id in player_pods.items() if pod_id == node_id), None)

            if player_id is None:
                return f"ERR|Tapped pod is not assigned to a user. Current assignments: {player_pods}"
                
            # Increase player tap count
            player_scores[player_id] += 1

            # Find available pods (those not currently assigned)
            assigned_pods = set(player_pods.values())
            available_pods = [node["id"] for node in nodes if node["id"] not in assigned_pods]

            # Assign a new pod to the player
            if available_pods:
                new_pod = random.choice(available_pods)
            else:
                # No free pods, assign the pod of the lowest-scoring player
                lowest_scoring_player = min(player_scores, key=player_scores.get)
                new_pod = player_pods[lowest_scoring_player]

            # Update player pod assignment
            player_pods[player_id] = new_pod
            color = PLAYER_COLORS.get(player_id, "#FFFFFF")
            
            return (
                f"NSTAT|{node_id}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}|{brighness}\n"
                f"NSTAT|{new_pod}|{color}|{'playStartSignal' if muted != 'MUTED' else 'NONE'}|{brighness}"
)

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
        return f"NSTAT|{parts[1]}|{new_color}|{buzz_melody}|{brighness}"
        
    return f"ERR|unknown exception for message {status_message}"

# Function to start a game
def start_game_OUTRUN():
    global active_nodes, game_name, muted, brighness
    active_nodes = {node["id"] for node in nodes}
    
    game_name = "OUTRUN"
    
    message = ""
    for i, node in enumerate(nodes):
        color = get_random_color()  # Generate a unique HEX color
        message += f"NSTAT|{node['id']}|{color}|{'playStartSignal' if muted != 'MUTED' else 'NONE'}|{brighness}\n"
        
    message += f":: {game_name} STARTED ::"
    return message.strip()

# Function to handle the start of the Randomize Me! game
def start_game_RANDOM():
    global current_blinking_pod, game_name, game_timer_start, muted, brighness
    
    game_name = 'RANDOM'
    game_timer_start = time.time()
    
    if len(nodes) > 0:
        current_blinking_pod = random.choice(nodes)["id"]  # Pick a random node
        color = get_random_color()  # Generate a unique HEX color
        return f"NSTAT|{current_blinking_pod}|{color}|{'playStartSignal' if muted != 'MUTED' else 'NONE'}|{brighness}\n:: {game_name} STARTED ::"
        
    return ""

# Function to handle the stop of the Randomize Me! game
def stop_game_RANDOM():
    global current_blinking_pod, game_name, game_timer_start, game_timer_end, muted
    
    game_name = None
    
    game_timer_end = time.time()
    
    if game_timer_start is None:
        duration = 0.0
    else:
        duration = game_timer_end - game_timer_start
        
    print(f"Game finished in {duration:.2f} seconds!")
    
    current_blinking_pod = None
    save_game_statistics("RANDOM", duration)
    return f"\nENDGAME|RANDOM|{duration:.2f} seconds!\n".join([f"NSTAT|{node['id']}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}|{brighness}" for node in nodes])

# Function to add a new node dynamically
def add_node(node_id):
    # Adds a new node to the nodes list if it doesn't already exist.
    for node in nodes:
        if node["id"] == node_id:
            return f"ERR|Node {node_id} already exists."
            
    nodes.append({"id": node_id, "status": "active"})
    print(f"Added new node: {node_id}")
    return f"HELLO|{node_id}|DON'T PANIC"
    
# Function to handle the start of the CHALLENGER game
def start_game_CHALLENGER(num_players):
    global game_name, game_timer_start, muted, brighness, player_pods, player_scores, nodes
    
    game_name = 'CHALLENGER'
    game_timer_start = time.time()
    player_scores = defaultdict(int) # Reset scores
    player_pods = {}
    
    num_players = min(int(num_players), len(nodes))  # Ensure valid player count
    
    if len(nodes) > 0:
        # Assign a random pod to each player
        assigned_pods = random.sample(nodes, num_players)
        player_pods = {i + 1: pod["id"] for i, pod in enumerate(assigned_pods)}  # {player_id: pod_id}
        
        # Construct message
        messages = [
            f"NSTAT|{pod['id']}|{PLAYER_COLORS.get(i+1, '#FFFFFF')}|{'playStartSignal' if muted != 'MUTED' else 'NONE'}|{brighness}"
            for i, pod in enumerate(assigned_pods)
        ]
        
        # Construct messages for unassigned pods (turn off)
        unassigned_messages = [
            f"NSTAT|{node['id']}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}|{brighness}"
            for node in nodes if node not in assigned_pods
        ]
        
        messages = messages + unassigned_messages

        messages.append(f":: {game_name} STARTED ::")
        
        return "\n".join(messages)  # Efficient string concatenation
        
    return ""

# Function to handle the stop of the CHALLENGER game
def stop_game_CHALLENGER():
    global current_blinking_pod, game_name, game_timer_start, game_timer_end, muted
    
    game_name = None
    
    game_timer_end = time.time()
    
    if game_timer_start is None:
        duration = 0.0
    else:
        duration = game_timer_end - game_timer_start
        
    print(f"Game finished in {duration:.2f} seconds!")
    
    save_game_statistics("CHALLENGER", duration)
    
    formatted_scores = json.dumps({str(k): v for k, v in player_scores.items()})  # Ensure string keys
    
    current_blinking_pod = None
    print(f"Player scores: {formatted_scores}")
    return f"\nENDGAME|CHALLENGER|{duration:.2f} seconds!|{formatted_scores}\n".join([f"NSTAT|{node['id']}|#000000|{'playDeviceDisconnect' if muted != 'MUTED' else 'NONE'}|{brighness}" for node in nodes])


def get_random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), 
                                        random.randint(0, 255), 
                                        random.randint(0, 255))

def save_game_statistics(game_name, time_played):
    """Save game statistics to the JSON file."""
    time_played = round(time_played, 0)  # Round to 2 decimal places
    
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
