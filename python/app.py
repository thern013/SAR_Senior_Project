import threading
from venv import logger
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
    time_spec = usrp.get_time_now().get_real_secs() + 2.0
    
    return usrp, time_spec
def get_rx_stream(usrp):
    # Create stream arguments
    rx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    rx_stream_args.args = "spp=1000"  # Setting for samples per packet
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

def recv_stream(usrp, rx_streamer, time_spec, quit_event):
    # Create Metadata
    rx_metadata = uhd.types.RXMetadata() 

    # Create Stream Command for continuous mode
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.time_spec = uhd.types.TimeSpec(time_spec)  # Set delayed start time
    stream_cmd.stream_now = False  # Do not stream immediately


   # Create a buffer to hold received samples
    recv_buffer = np.zeros(rx_streamer.get_max_num_samps(), dtype=np.complex64)
    recv_data = [[],[]]

    # Issue the stream command, but do not start immediately
    rx_streamer.issue_stream_cmd(stream_cmd)

    # Receive samples after the delay
    while not quit_event.is_set():
        rx_streamer.recv(recv_buffer, rx_metadata)

        # no error receieved fill buffer
        if rx_metadata.error_code == uhd.types.RXMetadataErrorCode.none:
            # print(f"rx_metadata.time: {rx_metadata.time_spec.get_real_secs()}")
            # print(f"internal clock time: {usrp.get_time_now().get_real_secs()}")
            recv_data[0].append(recv_buffer)
            recv_data[1].append(rx_metadata)


        # timeout error due to internal clock being less than the stream_cmd.time_spec
        elif rx_metadata.error_code == uhd.types.RXMetadataErrorCode.timeout:
            # logger.warning("Receiver error: %s, continuing...", rx_metadata.strerror())
            pass

    # Stop the continuous stream
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))

    plot_tx_rx_data(recv_data, "receiver")

def trans_stream(tx_streamer, time_spec, quit_event):
    # set buffer
    tx_buffer = np.exp(1j * 2 * np.pi * np.arange(1000) / 10).astype(np.complex64)
    tx_data = [[],[]]

    # set streamer and metadata
    tx_metadata = uhd.types.TXMetadata()

    # set meatadata args 
    tx_metadata.time_spec = uhd.types.TimeSpec(time_spec)  # convert to uhd format (get internal time in seconds)
    tx_metadata.has_time_spec = True

    # send stream until thread is stopped
    while not quit_event.is_set():
        samps = tx_streamer.send(tx_buffer, tx_metadata)
        if samps > 0:
            # print("Tx Time Spec:", tx_metadata.time_spec.get_real_secs())
            # print("Cur Time:", usrp.get_time_now().get_real_secs())
            # print(f"tx samples sent: {samps}")
            tx_data[0].append(tx_buffer)
            tx_data[1].append(tx_metadata)

    plot_tx_rx_data(tx_data, "transmit")

def plot_tx_rx_data(data, source):
    """
    Function to plot transmitted and received data.
    """
    # Ensure the data is not empty
    if not data:
        print("No data to plot.")
        return

    # Flatten the list of buffers into one large array for plotting
    data_real = np.concatenate([np.real(d) for d in data[0]])
    data_imag = np.concatenate([np.imag(d) for d in data[0]])

    plt.figure(figsize=(12, 6))
    plt.plot(data_real, label=f"{source} Real", color='b')
    plt.plot(data_imag, label=f"{source} Imag", color='r')
    plt.title(f"{source} Data")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    threads = []
    quit_event = threading.Event()
    duration = 1
    
    usrp, time_spec = usrp_init()

    rx_thread = threading.Thread(target=recv_stream, 
                                 args = (usrp, get_rx_stream(usrp), time_spec, quit_event),
                                 name="recv_stream",
                                 )
    tx_thread = threading.Thread(target=trans_stream,
                                 args=(get_tx_stream(usrp), time_spec, quit_event),
                                 name="trans_stream",)

    threads.append(rx_thread)
    threads.append(tx_thread)
    for thr in threads:
        thr.start()

    time.sleep(time_spec + 0.05)
    quit_event.set()
    for thr in threads:
        thr.join()


