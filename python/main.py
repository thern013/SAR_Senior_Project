import asyncio
import time
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
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

# Function to send data to a specific WebSocket connection
async def send_radio_response(websocket: WebSocket, path: str):
    try:
        while True:
            rx_amplitude = my_radio.imaging()
            rx_bytes = rx_amplitude.astype(np.uint8).tobytes()
            print(f'Rx_avg_pwr: {rx_amplitude}')
            await websocket.send_bytes(rx_bytes)

            await asyncio.sleep(2)  # Non-blocking sleep
    except WebSocketDisconnect:
        print(f"Client disconnected from {path}")
    except Exception as e:
        print(f"Error in WebSocket {path}: {e}")

# WebSocket endpoint for /amplitude/ws
@app.websocket("/amplitude/ws")
async def websocket_endpoint_1(websocket: WebSocket):
    await websocket.accept()
    await send_radio_response(websocket, "/amplitude/ws")

# WebSocket endpoint for /ws2
@app.websocket("/ws2")
async def websocket_endpoint_2(websocket: WebSocket):
    await websocket.accept()
    await send_radio_response(websocket, "/ws2")

# HTTP endpoint for fetching radio status
@app.get("/radarConfig")
async def get_radar_config():
    carrier_frequency, bandwidth, sample_rate, rx_gain, tx_gain = my_radio.get_config()
    jsonBody = {'carrier_frequency': carrier_frequency,
                'bandwidth': bandwidth,
                'sample_rate': sample_rate,
                'rx_gain': rx_gain,
                'tx_gain': tx_gain}
    
    return jsonBody

class RadarConfig(BaseModel):
    carrier_frequency: float
    bandwidth: float
    sample_rate: int
    rx_gain: int
    tx_gain: int
    
# HTTP endpoint for fetching radio status
@app.patch("/radarConfig")
async def set_radar_config(config: RadarConfig):
    my_radio.set_config(
    config.carrier_frequency, 
    config.bandwidth, 
    config.sample_rate, 
    config.rx_gain, 
    config.tx_gain
    )

    carrier_frequency, bandwidth, sample_rate, rx_gain, tx_gain = my_radio.get_config()
    jsonBody = {'carrier_frequency': carrier_frequency,
                'bandwidth': bandwidth,
                'sample_rate': sample_rate,
                'rx_gain': rx_gain,
                'tx_gain': tx_gain}
    
    return jsonBody