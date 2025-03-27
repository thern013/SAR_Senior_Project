import threading
from scipy.signal import correlate
import uhd
import numpy as np
from graph import matPlotting

class Radio:
    def __init__(self):
        self.usrp_init()
        self.set_rx_stream()
        self.set_tx_stream()

    def usrp_init(self):
        # Initialize the USRP device
        self.usrp = uhd.usrp.MultiUSRP()
        self.usrp.set_clock_source("internal")
        self.usrp.set_time_source("internal")
        self.usrp.set_master_clock_rate(32e6)
        self.usrp.set_time_now(uhd.types.TimeSpec(0.0))
        self.channel = 0

        self.usrp.set_rx_gain(76, self.channel)
        self.usrp.set_rx_freq(100e6, self.channel)
        self.usrp.set_rx_bandwidth(5e6, self.channel)

        self.usrp.set_tx_gain(89.75, self.channel)
        self.usrp.set_tx_freq(100e6, self.channel)
        self.usrp.set_tx_bandwidth(5e6, self.channel)

        self.delay = 2.000000
        self.time_spec = self.usrp.get_time_now().get_real_secs() + self.delay

        self.sample_rate = 2040*30

        print(f"""RX SETTINGS 
            antenna:    {self.usrp.get_rx_antenna(self.channel)}
            bandwidth:  {self.usrp.get_rx_bandwidth(self.channel)}
            frequency:  {self.usrp.get_rx_freq(self.channel)}
            freq range: {self.usrp.get_rx_freq_range(self.channel)}
            rx gain set:{self.usrp.get_rx_gain(self.channel)}
            gain names: {self.usrp.get_rx_gain_names(self.channel)}
            gain range: {self.usrp.get_rx_gain_range(self.channel)}
            lo enabled: {self.usrp.get_rx_lo_export_enabled('PGA', self.channel)}
        """)

        print(f"""TX SETTINGS 
            antenna:    {self.usrp.get_tx_antenna(self.channel)}
            bandwidth:  {self.usrp.get_tx_bandwidth(self.channel)}
            frequency:  {self.usrp.get_tx_freq(self.channel)}
            freq range: {self.usrp.get_tx_freq_range(self.channel)}
            tx gain set:{self.usrp.get_tx_gain(self.channel)}
            gain names: {self.usrp.get_tx_gain_names(self.channel)}
            gain range: {self.usrp.get_tx_gain_range(self.channel)}
            lo enabled: {self.usrp.get_tx_lo_export_enabled('PGA', self.channel)}
        """)
    
    def set_rx_stream(self):
        # Create stream arguments
        self.rx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
        # rx_stream_args.args = "spp=2040"  # Setting for samples per packet
        self.rx_stream_args.channels = [0]

        # create RX Streamer
        self.rx_streamer = self.usrp.get_rx_stream(self.rx_stream_args)


    def set_tx_stream(self):
        # Create stream arguments
        self.tx_stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
        # tx_stream_args.args = "spp=2040" 

        # create tx stream
        self.tx_streamer = self.usrp.get_tx_stream(self.tx_stream_args) 

    def get_usrp(self): return self.usrp
    def get_rx_stream(self): return self.rx_streamer
    def get_tx_stream(self): return self.tx_streamer
    def get_sample_rate(self): return self.sample_rate
    def get_time_spec(self): return self.time_spec
    def get_delay(self): return self.delay


def recv_stream(usrp, rx_streamer, time_spec, quit_event, rx_data, sample_rate):
    # Create Metadata
    rx_metadata = uhd.types.RXMetadata() 

    # Create Stream Command for continuous mode
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.time_spec = uhd.types.TimeSpec(time_spec)  # Set delayed start time
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

def trans_stream(usrp, tx_streamer, time_spec, quit_event, tx_data, sample_rate):
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


if __name__ == "__main__":
    radio = Radio()

    rx_data = [[], []]
    tx_data = [[], []]

    threads = []
    quit_event = threading.Event()
    duration = 1
    
    rx_thread = threading.Thread(target=recv_stream, 
                                 args = (radio.get_usrp(), radio.get_rx_stream(), radio.get_time_spec(), quit_event, rx_data, radio.get_sample_rate()),
                                 name="recv_stream",)
    threads.append(rx_thread)
    rx_thread.start()

    tx_thread = threading.Thread(target=trans_stream,
                                 args=(radio.get_usrp(), radio.get_tx_stream(), radio.get_time_spec(), quit_event, tx_data, radio.get_sample_rate()),
                                 name="trans_stream",)

    threads.append(tx_thread)
    tx_thread.start()
    print("threads started\n")
    
    while(radio.get_usrp().get_time_now().get_real_secs() < radio.get_delay() + 0.1):
        pass
    quit_event.set()
    for thr in threads:
        thr.join()
    print("threading join\n")

    print(f"""Rx data size: {len(rx_data[0])} Tx data size: {len(tx_data[0])}
        Rx data time: {rx_data[1][0].time_spec.get_full_secs() + rx_data[1][0].time_spec.get_frac_secs()}
        Tx data time: {tx_data[1][0].time_spec.get_full_secs() + tx_data[1][0].time_spec.get_frac_secs()}
    \n""")

        
    # plot_tx_rx_data(rx_data, tx_data, sample_rate)
    # corr_real, corr_imag = get_correlation(rx_data, tx_data, sample_rate)
    # plot_correlation(corr_real, corr_imag)

