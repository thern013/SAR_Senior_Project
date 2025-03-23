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

    usrp.set_rx_gain(76, channel)
    usrp.set_rx_freq(100e6, channel)
    usrp.set_rx_bandwidth(5e6, channel)

    usrp.set_tx_gain(89.75, channel)
    usrp.set_tx_freq(100e6, channel)
    usrp.set_tx_bandwidth(5e6, channel)

    delay = 2.0
    time_spec = usrp.get_time_now().get_real_secs() + delay

    sample_rate = 2040*30

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
    
    return usrp, time_spec, sample_rate, delay

def get_rx_stream(usrp):
    # Create stream arguments
    rx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    # rx_stream_args.args = "spp=2040"  # Setting for samples per packet
    rx_stream_args.channels = [0]

    # create RX Streamer
    rx_streamer = usrp.get_rx_stream(rx_stream_args)

    return rx_streamer

def get_tx_stream(usrp):
    # Create stream arguments
    tx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    # tx_stream_args.args = "spp=2040" 

    # create tx stream
    tx_streamer = usrp.get_tx_stream(tx_stream_args) 

    return tx_streamer

def recv_stream(rx_streamer, time_spec, quit_event, rx_data, sample_rate):
    # Create Metadata
    rx_metadata = uhd.types.RXMetadata() 

    # Create Stream Command for continuous mode
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.time_spec = uhd.types.TimeSpec(time_spec - 0.05)  # Set delayed start time
    stream_cmd.stream_now = False  # Do not stream immediately


   # Create a buffer to hold received samples
    recv_buffer = np.zeros(sample_rate, dtype=np.complex64)

    # Issue the stream command, but do not start immediately
    rx_streamer.issue_stream_cmd(stream_cmd)

    print(f"Receiving at: {usrp.get_time_now().get_real_secs()}")

    # Receive samples after the delay
    while not quit_event.is_set():
        samps = rx_streamer.recv(recv_buffer, rx_metadata)

        # no error receieved fill buffer
        if rx_metadata.error_code == uhd.types.RXMetadataErrorCode.none:
            rx_data[0].extend(recv_buffer)
            rx_data[1].append(rx_metadata)

        # timeout error due to internal clock being less than the stream_cmd.time_spec
        elif rx_metadata.error_code == uhd.types.RXMetadataErrorCode.timeout:
            pass
        if rx_metadata.error_code == uhd.types.RXMetadataErrorCode.overflow:
            print(f"time: {usrp.get_time_now().get_real_secs()} buffer overflow - cur size: {len(rx_data[0])} - last packet size: {samps}")
        if rx_metadata.error_code == uhd.types.RXMetadataErrorCode.late:
            print(f"time: {usrp.get_time_now().get_real_secs()} stream late ")

    # Stop the continuous stream
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))

    return rx_data

def trans_stream(tx_streamer, time_spec, quit_event, tx_data, sample_rate):
    # set buffer
    tx_buffer = get_pulse(sample_rate)

    # set streamer and metadata
    tx_metadata = uhd.types.TXMetadata()

    # set meatadata args 
    tx_metadata.time_spec = uhd.types.TimeSpec(time_spec)  # convert to uhd format (get internal time in seconds)
    tx_metadata.has_time_spec = True

    print(f"Transmitting at: {usrp.get_time_now().get_real_secs()}")

    # send stream until thread is stopped
    # while not quit_event.is_set():
    tx_streamer.send(tx_buffer, tx_metadata)

    tx_data[0].extend(tx_buffer)
    tx_data[1].append(tx_metadata)

    return tx_data


def get_pulse(sample_rate):
    max_samps = sample_rate
    
    # Create pulse1 and pulse2
    pulse1 = np.ones(max_samps // 2, dtype=np.complex64) * 5
    pulse2 = np.ones(max_samps // 2, dtype=np.complex64) * -5
    
    # Concatenate the pulses
    pulse = np.concatenate((pulse1, pulse2))

    return pulse

def get_correlation(rx_data, tx_data, sample_rate):
# Check if there is any data to plot
    if not rx_data[0] or not tx_data[0]:
        print("No data to calculate.")
        return

    rx_data_real = np.real(rx_data[0])
    rx_data_imag = np.imag(rx_data[0])

    tx_data_real = np.real(tx_data[0])
    tx_data_imag = np.imag(tx_data[0])

    # Compute cross-correlation between transmitted and received signals (real part)
    corr_real = correlate(tx_data_real, rx_data_real, mode='full')
    corr_imag = correlate(tx_data_imag, rx_data_imag, mode='full')

    # Find the lag at which the cross-correlation is maximum
    lag_real = np.argmax(np.abs(corr_real)) - len(tx_data_real) + 1
    lag_imag = np.argmax(np.abs(corr_imag)) - len(tx_data_imag) + 1

    time_lag_real = lag_real / sample_rate
    time_lag_imag = lag_imag / sample_rate

    print(f"Maximum correlation for real part: Lag = {lag_real} samples, Time Lag = {time_lag_real} seconds")
    print(f"Maximum correlation for imaginary part: Lag = {lag_imag} samples, Time Lag = {time_lag_imag} seconds")


    return corr_real, corr_imag

def plot_tx_rx_data(rx_data, tx_data):
    """
    Function to plot transmitted and received data and compute cross-correlation.
    """

    # Check if there is any data to plot
    if not rx_data[0] or not tx_data[0]:
        print("No data to plot.")
        return

    rx_data_real = np.real(rx_data[0])
    rx_data_imag = np.imag(rx_data[0])

    tx_data_real = np.real(tx_data[0])
    tx_data_imag = np.imag(tx_data[0])    

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

def plot_correlation(corr_real, corr_imag):
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


if __name__ == "__main__":
    rx_data = [[], []]
    tx_data = [[], []]

    threads = []
    quit_event = threading.Event()
    duration = 1
    
    usrp, time_spec, sample_rate, delay = usrp_init()

    rx_thread = threading.Thread(target=recv_stream, 
                                 args = (get_rx_stream(usrp), time_spec, quit_event, rx_data, sample_rate),
                                 name="recv_stream",)
    threads.append(rx_thread)
    rx_thread.start()

    tx_thread = threading.Thread(target=trans_stream,
                                 args=(get_tx_stream(usrp), time_spec, quit_event, tx_data, sample_rate),
                                 name="trans_stream",)

    threads.append(tx_thread)
    tx_thread.start()
    print("threads started")
    
    while(usrp.get_time_now().get_real_secs() < delay + 0.1):
        pass
    quit_event.set()
    for thr in threads:
        thr.join()
    print("threading join")

    print(f"Rx data size: {len(rx_data[0])} Tx data size: {len(tx_data[0])}")

    corr_real, corr_imag = get_correlation(rx_data, tx_data, sample_rate)
    
    plot_tx_rx_data(rx_data, tx_data)
    plot_correlation(corr_real, corr_imag)

