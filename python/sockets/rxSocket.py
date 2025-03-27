import asyncio
import websockets
import numpy as np

# Shared variable
complex_number = np.complex64(0 + 0j)  # Initial value
clients = set()  # Track connected clients

async def send_updates():
    """Continuously check for changes and notify clients."""
    global complex_number
    last_value = complex_number  # Store last sent value

    while True:
        await asyncio.sleep(0.1)  # Small delay to avoid high CPU usage

        if complex_number != last_value:
            last_value = complex_number
            message = complex_number.tobytes()
            if clients:  # Only send if clients are connected
                await asyncio.gather(*(client.send(message) for client in clients))
                print(f"Sent updated value: {complex_number}")

async def handle_client(websocket, path):
    """Handle incoming client connections."""
    global clients
    clients.add(websocket)
    try:
        await websocket.wait_closed()  # Keep connection open
    finally:
        clients.remove(websocket)  # Remove on disconnect

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("WebSocket server running on ws://localhost:8765")

    # Run the update task alongside the server
    await asyncio.gather(server.wait_closed(), send_updates())

asyncio.run(main())
