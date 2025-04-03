import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from pydantic import BaseModel
from radioManager.radio import Radio  # Import your class

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, customize as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)

# Instantiate the Radio class
my_radio = Radio()

# Store WebSocket connections
amplitude_connections = []
array_connections = []

async def handle_data():
    """Continuously fetch and send data to connected WebSocket clients."""
    while True:
        try:
            # Get both number and array from the imaging function
            amplitude, recv_data = my_radio.imaging()

            # Convert data to bytes
            rx_bytes = amplitude.astype(np.uint8).tobytes()
            recv_bytes = (recv_data * 32767).astype(np.int16).tobytes()

            # Send amplitude data and remove disconnected clients
            disconnected_clients = []
            for websocket in amplitude_connections:
                try:
                    await websocket.send_bytes(rx_bytes)
                except WebSocketDisconnect:
                    disconnected_clients.append(websocket)
                except Exception as e:
                    print(f"Error sending amplitude data: {e}")
                    disconnected_clients.append(websocket)

            # Remove closed connections
            for client in disconnected_clients:
                amplitude_connections.remove(client)
                print(f"Removed disconnected amplitude client.")

            # Send array data and remove disconnected clients
            disconnected_clients = []
            for websocket in array_connections:
                try:
                    await websocket.send_bytes(recv_bytes)
                except WebSocketDisconnect:
                    disconnected_clients.append(websocket)
                except Exception as e:
                    print(f"Error sending recvData: {e}")
                    disconnected_clients.append(websocket)

            # Remove closed connections
            for client in disconnected_clients:
                array_connections.remove(client)
                print(f"Removed disconnected array client.")

        except Exception as e:
            print(f"Unexpected error in handle_data loop: {e}")

        # Sleep before sending the next set of data
        await asyncio.sleep(2)  # Adjust as needed

@app.websocket("/amplitude/ws")
async def websocket_amplitude(websocket: WebSocket):
    """Handles WebSocket connections for amplitude data."""
    await websocket.accept()
    amplitude_connections.append(websocket)
    print(f"New client connected to /amplitude/ws")

    try:
        while True:
            await asyncio.sleep(0.1)  # Keep the connection alive
    except WebSocketDisconnect:
        amplitude_connections.remove(websocket)
        print(f"Client disconnected from /amplitude/ws")
    except Exception as e:
        print(f"Unexpected error in /amplitude/ws: {e}")

@app.websocket("/recvData/ws")
async def websocket_array(websocket: WebSocket):
    """Handles WebSocket connections for received data."""
    await websocket.accept()
    array_connections.append(websocket)
    print(f"New client connected to /recvData/ws")

    try:
        while True:
            await asyncio.sleep(0.1)  # Keep the connection alive
    except WebSocketDisconnect:
        array_connections.remove(websocket)
        print(f"Client disconnected from /recvData/ws")
    except Exception as e:
        print(f"Unexpected error in /recvData/ws: {e}")

# HTTP endpoint for fetching radio status
@app.get("/radarConfig")
async def get_radar_config():
    """Returns the current radar configuration."""
    carrier_frequency, bandwidth, sample_rate, rx_gain, tx_gain = my_radio.get_config()
    return {
        "carrier_frequency": carrier_frequency,
        "bandwidth": bandwidth,
        "sample_rate": sample_rate,
        "rx_gain": rx_gain,
        "tx_gain": tx_gain
    }

class RadarConfig(BaseModel):
    """Pydantic model for radar configuration input."""
    carrier_frequency: float
    bandwidth: float
    sample_rate: int
    rx_gain: int
    tx_gain: int

@app.patch("/radarConfig")
async def set_radar_config(config: RadarConfig):
    """Updates the radar configuration."""
    my_radio.set_config(
        config.carrier_frequency, 
        config.bandwidth, 
        config.sample_rate, 
        config.rx_gain, 
        config.tx_gain
    )

    # Return the updated config
    carrier_frequency, bandwidth, sample_rate, rx_gain, tx_gain = my_radio.get_config()
    return {
        "carrier_frequency": carrier_frequency,
        "bandwidth": bandwidth,
        "sample_rate": sample_rate,
        "rx_gain": rx_gain,
        "tx_gain": tx_gain
    }

# Start the background task when the app starts
@app.on_event("startup")
async def start_sending_data():
    """Starts the background data handling task when the server starts."""
    asyncio.create_task(handle_data())
