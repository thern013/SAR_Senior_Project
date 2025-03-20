import threading
import numpy as np
from datetime import datetime

def tx(i, signal):
    current_time = datetime.now().strftime("%H:%M:%S.%f")  # Current time in HH:MM:SS.mmmmmm format
    print(f"Txing at {current_time}: {signal[i]}")

def rx(i, rxBuffer, lock):
    current_time = datetime.now().strftime("%H:%M:%S.%f")  # Current time in HH:MM:SS.mmmmmm format
    with lock:
        rxBuffer.append(1)  # Append to shared list safely
    print(f"Rxing at {current_time}: {rxBuffer}")

if __name__ == "__main__":
    # Define signal parameters
    amplitude = 1
    period = 0.2
    sampling_rate = 100  # Sampling rate in Hz
    duration = 1  # Duration of the wave in seconds
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    signal = amplitude * np.sign(np.sin(2 * np.pi * t / period))

    # Shared buffer and lock for synchronization
    rxBuffer = []
    lock = threading.Lock()  # Lock for synchronization
    threads = []  # Store thread references

    # Start all threads in parallel
    for i in range(10):
        t1 = threading.Thread(target=tx, args=(i, signal))
        t2 = threading.Thread(target=rx, args=(i, rxBuffer, lock))
        t1.start()
        t2.start()
        threads.append(t1)
        threads.append(t2)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print(f"Final rxBuffer: {rxBuffer}")  # Print the final shared buffer
