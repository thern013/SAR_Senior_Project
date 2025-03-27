from flask import Flask
from flask_socketio import SocketIO, emit

# Create Flask app and SocketIO instance
app = Flask(__name__)
socketio = SocketIO(app)

# Global variable to store the rxData
rx_data_buffer = []

@app.route('/')
def index():
    return "SocketIO Server Running"

# Event that sends rxData[0] to Angular client
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    if rx_data_buffer:
        emit('rx_data', {'data': rx_data_buffer[0]})

# Function to update the rx_data_buffer with new data from the Radio class
def set_complex_number(rx_data):
    global rx_data_buffer
    rx_data_buffer = [rx_data]
    # You can trigger the sending of data here as well
    socketio.emit('rx_data', {'data': rx_data[0]})

if __name__ == '__main__':
    socketio.run(app, debug=True)
