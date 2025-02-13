import numpy as np
import matplotlib.pyplot as plt

# Define the file path
file_path = "gnuFileDump/gnuIQRx.exe"  # Update with the actual file path

# Read the binary file (assuming complex float32 format)
data = np.fromfile(open(file_path, "rb"), dtype=np.complex64)

# Extract real, imaginary, and magnitude components
real_part = np.real(data)
imag_part = np.imag(data)
magnitude = np.abs(data)

# Create a figure
plt.figure(figsize=(12, 6))

# Plot real and imaginary components on the same graph
plt.plot(real_part, label="Real Part", color="b", linestyle='-', alpha=0.7)
plt.plot(imag_part, label="Imaginary Part", color="r", linestyle='--', alpha=0.7)

# Add title and labels
plt.title("Real and Imaginary Components of the Received Signal")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.legend()

plt.xlim(100, 500)  # Zoom on x-axis from index 100 to 500
plt.ylim(-1, 1)  # Zoom on y-axis from -0.5 to 0.5

# Show the plots
plt.tight_layout()
plt.show()
