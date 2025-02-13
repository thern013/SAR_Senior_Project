import socket
import numpy as np
import matplotlib.pyplot as plt
import struct

# Define UDP parameters
udp_ip = "127.0.0.1"  # Local IP address (change if sending to another device)
udp_port = 8080       # Port on which GNU Radio is sending data
packet_size = 1472    # Packet size in bytes (for complex float32, each sample is 8 bytes)
timeout = 5           # Timeout in seconds

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

# Set socket timeout
sock.settimeout(timeout)

print(f"Listening for UDP packets on {udp_ip}:{udp_port}...")

# Initialize live plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(2, 1, figsize=(10, 6))
line1, = ax[0].plot([], [], 'b-', label="Real Part")  # Real part plot
line2, = ax[1].plot([], [], 'r-', label="Imaginary Part")  # Imaginary part plot

ax[0].set_title("Real Part of Signal")
ax[1].set_title("Imaginary Part of Signal")

for a in ax:
    a.set_xlim(0, 1024)  # Display first 1024 samples
    a.set_ylim(-1, 1)
    a.legend()
    a.grid()

# Function to process the received data and convert it to complex numbers
def process_data(data):
    # Convert the byte data to a numpy array of floats (single precision, i.e., float32)
    iq_data = np.frombuffer(data, dtype=np.float32)
    
    # Reconstruct complex signal (real + j*imaginary)
    complex_signal = iq_data[0::2] + 1j * iq_data[1::2]
    
    return complex_signal

try:
    while True:
        # Receive data from the UDP socket
        data, addr = sock.recvfrom(packet_size * 4)  # Receive packet (4 times packet_size for complex float32)

        if data:
            # Process the received data into complex numbers
            complex_signal = process_data(data)

            # Display the received signal in the terminal (first 10 samples)
            print("Received packet:")
            print("First 10 samples:")
            print(complex_signal[:10])  # Display first 10 complex samples
            print("")

            # Update the live plot
            x_vals = np.arange(len(complex_signal))  # X-axis values

            line1.set_xdata(x_vals)
            line1.set_ydata(complex_signal.real)

            line2.set_xdata(x_vals)
            line2.set_ydata(complex_signal.imag)

            ax[0].set_ylim(complex_signal.real.min(), complex_signal.real.max())
            ax[1].set_ylim(complex_signal.imag.min(), complex_signal.imag.max())

            plt.pause(0.01)  # Pause to update the plot

except socket.timeout:
    print(f"Timeout reached after {timeout} seconds. No data received.")
except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Close the socket when done
    sock.close()
    plt.ioff()  # Turn off interactive mode
    plt.show()  # Show the final plot
