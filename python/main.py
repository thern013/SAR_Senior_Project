import asyncio
import time
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
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

while True:
    rx_amplitude = my_radio.imaging()
# Function to send data to a specific WebSocket connection
async def send_radio_response(websocket: WebSocket, path: str):
    try:
        while True:
            rx_amplitude = my_radio.imaging()
            rx_bytes = rx_amplitude.astype(np.uint8).tobytes()
            await websocket.send_bytes(rx_bytes)

            await asyncio.sleep(3)  # Non-blocking sleep
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
@app.get("/sampleRate")
async def get_radio_status():
    response = my_radio.get_sample_rate()
    return {"sample_rate": response}
