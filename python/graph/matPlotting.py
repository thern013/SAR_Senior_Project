import matplotlib.pyplot as plt
import numpy as np


def plot_tx_rx_data(rx_data, tx_data, sample_rate):
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
    tx_data_real = tx_data_real

    t_rx = np.linspace(0, len(rx_data[0]), int(len(rx_data[0])))
    t_tx = np.linspace(0, len(tx_data[0]), int(len(tx_data[0])))

    # Plot the received and transmitted signals
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t_rx, rx_data_real, label=f"recv Real", color='b')
    # plt.plot(rx_data_imag, label=f"recv Imag", color='r')
    plt.title(f"Received Data")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(t_tx, tx_data_real, label=f"trans Real", color='b')
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