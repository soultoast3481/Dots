from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

# Initialize the Flask application
app = Flask(__name__)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app)

# Dictionary to store player information (position and color)
players = {}

# Dictionary to store trails for each player, using their session IDs
trails = {}  # Each player will have a separate trail dictionary

# Define the main route for the web page
@app.route('/')
def index():
    # Render the 'index.html' template when accessing the root URL
    return render_template('index.html')

# Event handler for when a client connects to the server
@socketio.on('connect')
def handle_connect():
    # Get the unique session ID for the player
    player_id = request.sid

    # Generate a random color for the new player
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))

    # Initialize player with random starting coordinates and the chosen color
    players[player_id] = {'x': random.randint(0, 500), 'y': random.randint(0, 500), 'color': color}

    # Initialize an empty trail for the player in the trails dictionary
    trails[player_id] = []

    # Print connection info
    print(f"[CONNECT] Player {player_id} has connected with color {color} at ({players[player_id]['x']}, {players[player_id]['y']}).")

    # Broadcast the updated player list to all clients
    emit('update_players', players, broadcast=True)

# Event handler for when a client disconnects from the server
@socketio.on('disconnect')
def handle_disconnect():
    # Get the player's session ID
    player_id = request.sid

    # Remove player information from both players and trails dictionaries
    if player_id in players:
        print(f"[DISCONNECT] Player {player_id} has disconnected.")
        del players[player_id]

    if player_id in trails:
        del trails[player_id]

    # Broadcast the updated player list to all clients
    emit('update_players', players, broadcast=True)

# Event handler for handling player movements
@socketio.on('move')
def handle_move(data):
    # Get the player's session ID
    player_id = request.sid

    # Check if the player exists in the players dictionary
    if player_id in players:
        # Extract new coordinates from the received data
        x, y = data['x'], data['y']

        # Append the current position to the player's trail
        trails[player_id].append({'x': players[player_id]['x'], 'y': players[player_id]['y'], 'opacity': 1.0})

        # Limit the trail to a maximum of 4 dots
        if len(trails[player_id]) > 4:
            trails[player_id].pop(0)

        # Update player's position with new coordinates
        old_x, old_y = players[player_id]['x'], players[player_id]['y']
        players[player_id]['x'], players[player_id]['y'] = x, y

        # Print movement info
        print(f"[MOVE] Player {player_id} moved from ({old_x}, {old_y}) to ({x}, {y}). Trail: {trails[player_id]}")

        # Emit the updated player positions to all clients
        emit('update_players', players, broadcast=True)

        # Emit the updated trails to all clients
        emit('update_trails', trails, broadcast=True)

    # Print the current state of all players
    print(f"[INFO] Current Players: {players}")
    print(f"[INFO] Current Trails: {trails}")

# Main entry point to run the Flask-SocketIO server
if __name__ == '__main__':
    # Run the application with SocketIO enabled on all IP addresses of the host machine
    print("[SERVER STARTED] SocketIO server is running...")
    socketio.run(app, host='0.0.0.0')
