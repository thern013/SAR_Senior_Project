import socket
import numpy as np
import time

# Define UDP target
UDP_IP = "127.0.0.1"  # Change if sending to another device
UDP_PORT = 8080       # GNU Radio listening port
PACKET_SIZE = 1472    # Packet size in bytes

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Complex sine wave parameters
fs = 1000  # Sampling frequency in Hz
f = 5      # Sine wave frequency in Hz
duration = 2  # Duration in seconds
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

# Generate complex sine wave (I/Q data)
complex_wave = np.exp(1j * 2 * np.pi * f * t).astype(np.complex64)  # float32 complex

# Convert to bytes
iq_bytes = complex_wave.tobytes()

# Send packets in chunks of 1472 bytes
for i in range(0, len(iq_bytes), PACKET_SIZE):
    packet = iq_bytes[i:i+PACKET_SIZE]
    sock.sendto(packet, (UDP_IP, UDP_PORT))
    time.sleep((1 / fs) * (PACKET_SIZE // 8))  # Control transmission rate

print("Complex sine wave packets sent to GNU Radio.")

# Close socket
sock.close()
