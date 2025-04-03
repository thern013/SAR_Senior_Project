import threading
from scipy.signal import correlate
import uhd
import numpy as np
from graph import matPlotting
import time
import math

class Radio:
    def __init__(self):
        self.usrp_init()
        self.set_rx_stream()
        self.set_rx_metadata()
        self.set_rx_stream_cmd()
        self.set_tx_stream()
        self.set_tx_metadata()

    def usrp_init(self):
        self.rx_data = [[],[]]
        self.tx_data = [[],[]]
        self.freq = 2.4e9
        self.bandwith = 5e6
        self.sample_rate = int(2048)
        self.cpu_format = "fc32"
        self.otw_format = "sc16"
        self.rx_gain = 76 # max 76
        self.tx_gain = 55 # max 89.75 

        # Initialize the USRP device
        self.usrp = uhd.usrp.MultiUSRP()
        self.usrp.set_clock_source("internal")
        self.usrp.set_time_source("internal")
        self.usrp.set_master_clock_rate(32e6)
        self.usrp.set_time_now(uhd.types.TimeSpec(0.0))
        self.channel = 0

        self.usrp.set_rx_gain(self.rx_gain, self.channel)
        self.usrp.set_rx_freq(self.freq, self.channel)
        self.usrp.set_rx_bandwidth(self.bandwith, self.channel)

        self.usrp.set_tx_gain(self.tx_gain, self.channel)
        self.usrp.set_tx_freq(self.freq, self.channel)
        self.usrp.set_tx_bandwidth(self.bandwith, self.channel)

        self.delay = 0.01
        self.time_spec = self.usrp.get_time_now().get_real_secs() + self.delay
        self.pulse = self.get_pulse()
        self.print_radio_specs()

    def set_rx_stream(self):
        self.rx_stream_args = uhd.usrp.StreamArgs(self.cpu_format, self.otw_format)
        self.rx_stream_args.channels = [0]
        self.rx_streamer = self.usrp.get_rx_stream(self.rx_stream_args)

    def set_rx_metadata(self): 
        self.rx_metadata = uhd.types.RXMetadata() 

    def set_rx_stream_cmd(self):
        self.rx_stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
        self.set_rx_stream_cmd_time_spec()
        self.rx_stream_cmd.stream_now = False  # Do not stream immediately

    def set_rx_stream_cmd_time_spec(self):
        self.rx_stream_cmd.time_spec = uhd.types.TimeSpec(self.time_spec)  # Set delayed start time

    def set_tx_stream(self):
        self.tx_stream_args = uhd.usrp.StreamArgs(self.cpu_format, self.otw_format)
        self.tx_streamer = self.usrp.get_tx_stream(self.tx_stream_args) 

    def set_tx_metadata(self):
        self.tx_metadata = uhd.types.TXMetadata()
        self.set_tx_time_spec()
        self.tx_metadata.has_time_spec = True
        self.tx_metadata.start_of_burst = True  # Indicate start of burst
        self.tx_metadata.end_of_burst = True    # Ensure TX stops at the end of burst

    def set_tx_time_spec(self):
        self.tx_metadata.time_spec = uhd.types.TimeSpec(self.time_spec)  

    def get_time(self): return self.usrp.get_time_now().get_real_secs()

    def get_config(self):
        return round(self.freq * 1e-9, 4), self.bandwith * 1e-6, self.sample_rate, self.rx_gain, self.tx_gain
    
    def set_config(self, freq, bandwith, sample_rate, rx_gain, tx_gain):
        self.set_carrier_freq(freq)
        self.set_bandwidth(bandwith)
        self.set_sample_rate(sample_rate)
        self.set_rx_gain(rx_gain)
        self.set_tx_gain(tx_gain)

    def set_carrier_freq(self, freq):   
        self.freq = freq * 1e9
        self.usrp.set_rx_freq(self.freq, self.channel)
        self.usrp.set_tx_freq(self.freq, self.channel)

    def set_bandwidth(self, bandwidth): 
        self.bandwith = bandwidth * 1e6
        self.usrp.set_rx_bandwidth(self.bandwith, self.channel)
        self.usrp.set_tx_bandwidth(self.bandwith, self.channel)

    def set_sample_rate(self, sample_rate):    
        self.sample_rate = int(sample_rate)

    def set_rx_gain(self, rx_gain):    self.rx_gain = rx_gain
    def set_tx_gain(self, tx_gain):    self.tx_gain = tx_gain
    
    def set_new_time_spec(self): 
        self.time_spec = self.get_time() + self.delay
        self.set_rx_stream_cmd_time_spec()
        self.rx_metadata.reset()
        self.set_tx_time_spec()


    def recv_stream(self, recv_event, tx_event, main_event):
        # Create a buffer to hold received samples
        recv_buffer = np.zeros(self.sample_rate, dtype=np.complex64)


        # Issue the stream command, but do not start immediately
        self.rx_streamer.issue_stream_cmd(self.rx_stream_cmd)
        # Receive samples after the delay

        while not tx_event.is_set():
            samps = self.rx_streamer.recv(recv_buffer, self.rx_metadata)

            # no error receieved fill buffer
            if self.rx_metadata.error_code == uhd.types.RXMetadataErrorCode.none:
                self.rx_data[0].extend(recv_buffer)
                self.rx_data[1].append(self.rx_metadata)

            # timeout error due to internal clock being less than the stream_cmd.time_spec
            elif self.rx_metadata.error_code == uhd.types.RXMetadataErrorCode.timeout:
                print(f"Delay till: {self.time_spec} time: {self.usrp.get_time_now().get_real_secs()}")
            elif self.rx_metadata.error_code == uhd.types.RXMetadataErrorCode.overflow:
                print(f"time: {self.usrp.get_time_now().get_real_secs()} buffer overflow - cur size: {len(self.rx_data[0])} - last packet size: {samps}")
            elif self.rx_metadata.error_code == uhd.types.RXMetadataErrorCode.late:
                print(f"time: {self.usrp.get_time_now().get_real_secs()} stream late ")

        self.rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))
        recv_event.set()
        
    def trans_stream(self, tx_event, main_event):
        # set buffer
        tx_buffer = self.pulse

        # send stream until thread is stopped
        self.tx_streamer.send(tx_buffer, self.tx_metadata)
        # print(f"transmitting")
        self.tx_data[0].extend(tx_buffer)
        self.tx_data[1].append(self.tx_metadata)

        time.sleep(0.0)
        tx_event.set()

    def get_pulse(self):        
        f = 10  # Frequency in Hz
        duration = 10/f  # Duration in seconds

        # Generate time array
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        # Generate the in-phase (I) and quadrature (Q) components with float32 precision
        I = np.cos(2 * np.pi * f * t).astype(np.float32)  # Cosine wave for I
        Q = np.sin(2 * np.pi * f * t).astype(np.float32)  # Sine wave for Q

        # Combine into a complex signal of type 
        pulse = (I + 1j * Q).astype(np.complex64) #fc32 is a np.complex64

        return pulse

    def getAmplitude(self):
        if not self.rx_data[0] or not self.tx_data[0]:
            print("No data to calculate.")
            return

        rx_avg_pwr = np.mean(np.abs(self.rx_data[0][-self.sample_rate:])**2) * (255 / 2)
        tx_avg_pwr = np.mean(np.abs(self.tx_data[0])**2) * 255

        return rx_avg_pwr, tx_avg_pwr
    
    def getPhaseAngle(self):
        if not self.rx_data[0] or not self.tx_data[0]:
            print("No data to calculate.")
            return
        
        rx_phase = np.angle(self.rx_data[0])
        tx_phase = np.angle(self.tx_data[0])

        return rx_phase, tx_phase
    
    def get_correlation(self):
        if not self.rx_data[0] or not self.tx_data[0]:
            print("No data to calculate.")
            return

        rx_data_real = np.real(self.rx_data[0])
        rx_data_imag = np.imag(self.rx_data[0])

        tx_data_real = np.real(self.tx_data[0])
        tx_data_imag = np.imag(self.tx_data[0])

        # Compute cross-correlation between transmitted and received signals (real part)
        corr_real = correlate(tx_data_real, rx_data_real, mode='full')
        corr_imag = correlate(tx_data_imag, rx_data_imag, mode='full')

        # Find the lag at which the cross-correlation is maximum
        lag_real = np.argmax(np.abs(corr_real)) - len(tx_data_real) + 1
        lag_imag = np.argmax(np.abs(corr_imag)) - len(tx_data_imag) + 1

        time_lag_real = lag_real / self.sample_rate
        time_lag_imag = lag_imag / self.sample_rate

        print(f"Maximum correlation for real part: Lag = {lag_real} samples, Time Lag = {time_lag_real} seconds")
        print(f"Maximum correlation for imaginary part: Lag = {lag_imag} samples, Time Lag = {time_lag_imag} seconds")


        return corr_real, corr_imag

    def reset_buffers(self):
        for arr in self.rx_data:
            arr.clear()
        for arr in self.tx_data:
            arr.clear()

    def imaging(self):
        self.reset_buffers()
        
        threads = []
        recv_event = threading.Event()
        tx_event = threading.Event()
        main_event = threading.Event()
        
        recv_event.clear()
        tx_event.clear()
        main_event.clear()


        rx_thread = threading.Thread(target=self.recv_stream, 
                                    args = (recv_event, tx_event, main_event),
                                    name="recv_stream",)
        threads.append(rx_thread)

        tx_thread = threading.Thread(target=self.trans_stream,
                                    args=(tx_event, main_event),
                                    name="trans_stream",)
    
        threads.append(tx_thread)

        self.set_new_time_spec()    # set new time_spec  

        for thr in threads:
            thr.start()
        
        # allow thread start up incase you have a sad excuse of a machine
        recv_event.wait()   # wait for recv thread

        for thr in threads:
            thr.join()
        
        if len(self.rx_data[0]) <= self.sample_rate:
            print(f'sample was too small')
            self.imaging()

        rx_avg_pwr, tx_avg_pwr =  self.getAmplitude()

        # corr_real, corr_imag = get_correlation(self.rx_data, self.tx_data, radio.get_sample_rate())
        return rx_avg_pwr, np.real(self.rx_data[0][-2048:])

    def print_radio_specs(self):
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
    
        print(f"INFO:     Radio Initialized")
    
    def print_results(self):
        print(f"""Rx data size: {len(self.rx_data[0])} Tx data size: {len(self.tx_data[0])}
            Tx/Rx dealy : {self.time_spec}
            Rx data time: {self.rx_data[1][0].time_spec.get_full_secs() + self.rx_data[1][0].time_spec.get_frac_secs()}
            Tx data time: {self.tx_data[1][0].time_spec.get_full_secs() + self.tx_data[1][0].time_spec.get_frac_secs()}
            Rx precision: {self.rx_data[0][0]}
            Tx Precision: {self.tx_data[0][0]}
        \n""")
