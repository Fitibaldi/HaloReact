from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_TOPIC_ACTION = "pod_action"
MQTT_TOPIC_STATUS = "pod_status"

# Global variable to store the game result
game_result = None
result_lock = threading.Lock()

# MQTT Callback for message
def on_message(client, userdata, msg):
    global game_result
    if msg.topic == MQTT_TOPIC_ACTION:
        payload = msg.payload.decode()
        if payload.startswith("ENDGAME"):
            with result_lock:
                game_result = payload.split("|")[1]  # Extract the time (e.g., "4:42")

# Flask Route for Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Flask Route to Start the Game
@app.route("/start_game", methods=["POST"])
def start_game():
    global game_result
    with result_lock:
        game_result = None  # Reset game result when the game starts
    data = request.get_json()
    mute_status = data.get("mute", "MUTE")
    client.publish(MQTT_TOPIC_STATUS, f"START|OUTRUN|{mute_status}")
    return jsonify({"message": "Game started!"}), 200

# Flask Route to Get Timer Result
@app.route("/get_timer", methods=["GET"])
def get_timer():
    global game_result
    with result_lock:
        if game_result:
            return jsonify({"time": game_result}), 200
    return jsonify({"time": "Timer running..."}), 200

# Flask Route to Start the Randomize Me! Game
@app.route("/start_random_game", methods=["POST"])
def start_random_game():
    global game_result
    with result_lock:
        game_result = None  # Reset game result when starting a new game
    data = request.get_json()
    mute_status = data.get("mute", "MUTE")
    client.publish(MQTT_TOPIC_STATUS, f"START|RANDOM|{mute_status}")
    return jsonify({"message": "Randomize Me! game started"}), 200

# Flask Route to End the Randomize Me! Game
@app.route("/end_random_game", methods=["POST"])
def end_random_game():
    client.publish(MQTT_TOPIC_STATUS, "STOP|RANDOM")
    return jsonify({"message": "Randomize Me! game ended"}), 200

# MQTT Client Setup
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC_ACTION)

# Start MQTT loop in a separate thread
def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
