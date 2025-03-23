import threading
from venv import logger
from scipy.signal import square
from scipy.signal import correlate
from scipy import signal
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
    channel = 0

    usrp.set_rx_gain(0, channel)
    usrp.set_rx_freq(100e6, channel)
    usrp.set_rx_bandwidth(5e6, channel)

    usrp.set_tx_gain(89, channel)
    usrp.set_tx_freq(100e6, channel)
    usrp.set_tx_bandwidth(5e6, channel)

    delay = 2.0
    time_spec = usrp.get_time_now().get_real_secs() + delay

    max_samples = 2040*30

    print(f"""RX SETTINGS 
        antenna:    {usrp.get_rx_antenna(channel)}
        bandwidth:  {usrp.get_rx_bandwidth(channel)}
        frequency:  {usrp.get_rx_freq(channel)}
        freq range: {usrp.get_rx_freq_range(channel)}
        rx gain set:{usrp.get_rx_gain(channel)}
        gain names: {usrp.get_rx_gain_names(channel)}
        gain range: {usrp.get_rx_gain_range(channel)}
        lo enabled: {usrp.get_rx_lo_export_enabled('PGA', channel)}
    """)

    print(f"""TX SETTINGS 
        antenna:    {usrp.get_tx_antenna(channel)}
        bandwidth:  {usrp.get_tx_bandwidth(channel)}
        frequency:  {usrp.get_tx_freq(channel)}
        freq range: {usrp.get_tx_freq_range(channel)}
        tx gain set:{usrp.get_tx_gain(channel)}
        gain names: {usrp.get_tx_gain_names(channel)}
        gain range: {usrp.get_tx_gain_range(channel)}
        lo enabled: {usrp.get_tx_lo_export_enabled('PGA', channel)}
    """)
    
    return usrp, time_spec, max_samples

def get_rx_stream(usrp):
    # Create stream arguments
    rx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    rx_stream_args.args = "spp=2040"  # Setting for samples per packet
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

def recv_stream(rx_streamer, time_spec, quit_event, rx_data, max_samples):
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
    while usrp.get_time_now().get_real_secs() < time_spec:
        pass 
    print(f"begin recv stream: {usrp.get_time_now().get_real_secs()}")
    while len(rx_data[0]) < max_samples:  
        samps = rx_streamer.recv(recv_buffer, rx_metadata)

        # no error receieved fill buffer
        if rx_metadata.error_code == uhd.types.RXMetadataErrorCode.none:
            rx_data[0].extend(recv_buffer)
            rx_data[1].append(rx_metadata)

        # timeout error due to internal clock being less than the stream_cmd.time_spec
        elif rx_metadata.error_code == uhd.types.RXMetadataErrorCode.timeout:
            pass

    # Stop the continuous stream
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))
    quit_event.set()
    print(f"end recv stream: {usrp.get_time_now().get_real_secs()} size: {len(rx_data[0])}")
    return rx_data

def trans_stream(tx_streamer, time_spec, tx_data, max_samples):
    # set buffer
    tx_buffer = get_pulse(max_samples)
    # set streamer and metadata
    tx_metadata = uhd.types.TXMetadata()

    # set meatadata args 
    tx_metadata.time_spec = uhd.types.TimeSpec(time_spec)  # convert to uhd format (get internal time in seconds)
    tx_metadata.has_time_spec = True

    # send stream until thread is stopped
    # while usrp.get_time_now().get_real_secs() < time_spec:
    #     pass
    while not quit_event.is_set():
        samps = tx_streamer.send(tx_buffer, tx_metadata)
        print(f"sent packet at: {usrp.get_time_now().get_real_secs()}  size: {samps}")
        tx_data[0].extend(tx_buffer)
        tx_data[1].append(tx_metadata)

    return tx_data


def get_pulse(max_samples):
    max_samps = max_samples
    
    # Create pulse1 and pulse2
    pulse1 = np.zeros(max_samps // 2, dtype=np.complex64)
    pulse2 = np.zeros(max_samps // 2, dtype=np.complex64)
    
    # Concatenate the pulses
    pulse = np.concatenate((pulse1, pulse2))

    return pulse


def plot_tx_rx_data(rx_data, tx_data):
    """
    Function to plot transmitted and received data and compute cross-correlation.
    """

    # Check if there is any data to plot
    if not rx_data[0] or not tx_data[0]:
        print("No data to plot.")
        return

    # Flatten the list of buffers into one large array for plotting
    rx_data_real = ([np.real(d) for d in rx_data[0]])
    rx_data_imag = ([np.imag(d) for d in rx_data[0]])

    tx_data_real = ([np.real(d) for d in tx_data[0]])
    tx_data_imag = ([np.imag(d) for d in tx_data[0]])

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
    # plt.plot(rx_data_imag, label=f"recv Imag", color='r')
    plt.title(f"Received Data")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(tx_data_real, label=f"trans Real", color='b')
    # plt.plot(tx_data_imag, label=f"trans Imag", color='r')
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
    
    usrp, time_spec, max_samples = usrp_init()

    rx_thread = threading.Thread(target=recv_stream, 
                                 args = (get_rx_stream(usrp), time_spec, quit_event, rx_data, max_samples),
                                 name="recv_stream",)
    tx_thread = threading.Thread(target=trans_stream,
                                 args=(get_tx_stream(usrp), time_spec, tx_data, max_samples),
                                 name="trans_stream",)

    threads.append(rx_thread)
    threads.append(tx_thread)
    for thr in threads:
        thr.start()

    print("threading start")
    

    while not quit_event.is_set():
        for thr in threads:
            thr.join()

    print("threading join")
    plot_tx_rx_data(rx_data, tx_data)

