import threading
from venv import logger
from scipy.signal import chirp
from scipy.signal import correlate
import uhd
import matplotlib.pyplot as plt
import numpy as np
import time

def usrp_init():
    # Initialize the USRP device
    usrp = uhd.usrp.MultiUSRP()
    usrp.set_clock_source("internal")
    usrp.set_time_source("internal")
    usrp.set_master_clock_rate(32e6)
    usrp.set_time_now(uhd.types.TimeSpec(0.0))
    usrp.set_rx_gain(50, 0)
    usrp.set_tx_gain(50, 0)
    
    time_spec = usrp.get_time_now().get_real_secs() + 2.0
    
    return usrp, time_spec
def get_rx_stream(usrp):
    # Create stream arguments
    rx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    rx_stream_args.args = "spp=200"  # Setting for samples per packet
    rx_stream_args.channels = [0]

    # create RX Streamer
    rx_streamer = usrp.get_rx_stream(rx_stream_args)

    return rx_streamer

def get_tx_stream(usrp):
    # Create stream arguments
    tx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    tx_stream_args.args = "spp=200" 

    # create tx stream
    tx_streamer = usrp.get_tx_stream(tx_stream_args) 

    return tx_streamer

def recv_stream(rx_streamer, time_spec, quit_event, rx_data):
    # Create Metadata
    rx_metadata = uhd.types.RXMetadata() 

    # Create Stream Command for continuous mode
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.time_spec = uhd.types.TimeSpec(time_spec)  # Set delayed start time
    stream_cmd.stream_now = False  # Do not stream immediately


   # Create a buffer to hold received samples
    recv_buffer = np.zeros(rx_streamer.get_max_num_samps(), dtype=np.complex64)

    # Issue the stream command, but do not start immediately
    rx_streamer.issue_stream_cmd(stream_cmd)

    # Receive samples after the delay
    while not quit_event.is_set():
        samps = rx_streamer.recv(recv_buffer, rx_metadata)

        # no error receieved fill buffer
        if rx_metadata.error_code == uhd.types.RXMetadataErrorCode.none:
            rx_data[0].append(recv_buffer)
            rx_data[1].append(rx_metadata)
            print(f"recv packet at: {usrp.get_time_now().get_real_secs()} size: {samps}")

        # timeout error due to internal clock being less than the stream_cmd.time_spec
        elif rx_metadata.error_code == uhd.types.RXMetadataErrorCode.timeout:
            pass

    # Stop the continuous stream
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))

    return rx_data

def trans_stream(tx_streamer, time_spec, quit_event, tx_data):
    # set buffer
    tx_buffer, t = get_pulse()

    # set streamer and metadata
    tx_metadata = uhd.types.TXMetadata()

    # set meatadata args 
    tx_metadata.time_spec = uhd.types.TimeSpec(time_spec)  # convert to uhd format (get internal time in seconds)
    tx_metadata.has_time_spec = True

    # send stream until thread is stopped
    while not quit_event.is_set():
        while usrp.get_time_now().get_real_secs() < time_spec:
            pass
        samps = tx_streamer.send(tx_buffer, tx_metadata)
        print(f"sent packet at: {usrp.get_time_now().get_real_secs()}  size: {samps}")
        if samps > 0:
            tx_data[0].append(tx_buffer)
            tx_data[1].append(tx_metadata)

    return tx_data


def get_pulse(duration=1e-3, sample_rate=60e6):
    """
    Generate a square wave pulse signal with 3 periods within the given duration.

    Args:
    - duration: Duration of the pulse (in seconds).
    - sample_rate: The sampling rate for the signal (in Hz).

    Returns:
    - pulse_signal: The square wave pulse signal.
    - t: Time vector for plotting.
    """
    # Calculate the frequency of the square wave to fit 3 periods within the duration
    frequency = 2 / duration  # 3 periods in the duration

    # Time vector for the pulse signal
    t = np.arange(0, duration, 1/sample_rate)

    # Generate a square wave with the given frequency
    pulse_signal = 0.5 * (1 + np.sign(np.sin(2 * np.pi * frequency * t)))  # Square wave

    return pulse_signal, t


def plot_tx_rx_data(rx_data, tx_data):
    """
    Function to plot transmitted and received data and compute cross-correlation.
    """

    # Check if there is any data to plot
    if not rx_data[0] or not tx_data[0]:
        print("No data to plot.")
        return

    # Flatten the list of buffers into one large array for plotting
    rx_data_real = np.concatenate([np.real(d) for d in rx_data[0]])
    rx_data_imag = np.concatenate([np.imag(d) for d in rx_data[0]])

    tx_data_real = np.concatenate([np.real(d) for d in tx_data[0]])
    tx_data_imag = np.concatenate([np.imag(d) for d in tx_data[0]])

    # Compute cross-correlation between transmitted and received signals (real part)
    corr_real = correlate(tx_data_real, rx_data_real, mode='full')
    corr_imag = correlate(tx_data_imag, rx_data_imag, mode='full')

    # Find the lag at which the cross-correlation is maximum
    lag_real = np.argmax(np.abs(corr_real)) - len(tx_data_real) + 1
    lag_imag = np.argmax(np.abs(corr_imag)) - len(tx_data_imag) + 1

    print(f"Maximum correlation for real part: Lag = {lag_real} samples")
    print(f"Maximum correlation for imaginary part: Lag = {lag_imag} samples")

    # Plot the received and transmitted signals
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(rx_data_real, label=f"recv Real", color='b')
    plt.plot(rx_data_imag, label=f"recv Imag", color='r')
    plt.title(f"Received Data")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(tx_data_real, label=f"trans Real", color='b')
    plt.plot(tx_data_imag, label=f"trans Imag", color='r')
    plt.title(f"Transmitted Data")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Plot cross-correlation
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(corr_real, label='Cross-correlation (Real)')
    plt.title('Cross-correlation of Real Part')
    plt.xlabel('Sample Lag')
    plt.ylabel('Correlation Amplitude')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(corr_imag, label='Cross-correlation (Imag)')
    plt.title('Cross-correlation of Imaginary Part')
    plt.xlabel('Sample Lag')
    plt.ylabel('Correlation Amplitude')
    plt.legend()

    plt.tight_layout()
    plt.show()



def plot_chirp(chirp_signal, t):
    """
    Function to plot the chirp signal (Real and Imaginary parts).
    """
    # Ensure the chirp_signal is not empty
    if len(chirp_signal) == 0:
        print("Chirp signal is empty.")
        return

    # Extract the real and imaginary parts of the chirp signal
    chirp_real = np.real(chirp_signal)
    chirp_imag = np.imag(chirp_signal)

    # Plot the chirp signal
    plt.figure(figsize=(12, 6))

    # Plot real part of the chirp signal
    plt.subplot(2, 1, 1)
    plt.plot(t, chirp_real, label="Chirp Real", color='b')
    plt.title("Chirp Signal - Real Part")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.legend()

    # Plot imaginary part of the chirp signal
    plt.subplot(2, 1, 2)
    plt.plot(t, chirp_imag, label="Chirp Imag", color='r')
    plt.title("Chirp Signal - Imaginary Part")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.tight_layout()
    plt.show()

def calculate_snr(tx_data, rx_data):
    # Flatten tx and rx data
    tx_data_flat = np.concatenate([np.real(d) for d in tx_data[0]])
    rx_data_flat = np.concatenate([np.real(d) for d in rx_data[0]])

    # Signal power (transmitted signal)
    signal_power = np.mean(np.abs(tx_data_flat)**2)

    # Noise power (difference between received and transmitted signal)
    noise_power = np.mean(np.abs(rx_data_flat - tx_data_flat)**2)

    # Compute SNR
    snr = 10 * np.log10(signal_power / noise_power)
    print(f"SNR: {snr} dB")
    return snr

if __name__ == "__main__":
    rx_data = [[], []]
    tx_data = [[], []]

    threads = []
    quit_event = threading.Event()
    duration = 1
    
    usrp, time_spec = usrp_init()

    rx_thread = threading.Thread(target=recv_stream, 
                                 args = (get_rx_stream(usrp), time_spec, quit_event, rx_data),
                                 name="recv_stream",)
    tx_thread = threading.Thread(target=trans_stream,
                                 args=(get_tx_stream(usrp), time_spec, quit_event, tx_data),
                                 name="trans_stream",)

    threads.append(rx_thread)
    threads.append(tx_thread)
    for thr in threads:
        thr.start()

    print("threading start")
    

    time.sleep(time_spec + 0.0005)
    quit_event.set()
    for thr in threads:
        thr.join()

    print("threading join")
    plot_tx_rx_data(rx_data, tx_data)

