FROM python:3.7

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    libboost-all-dev \
    libusb-1.0-0-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

    # Copy the requirements.txt file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone UHD and build it
RUN git clone https://github.com/EttusResearch/uhd.git && \
    cd uhd/host && \
    mkdir build && \
    cd build && \
    cmake -DENABLE_TESTS=OFF -DENABLE_C_API=OFF -DENABLE_PYTHON_API=ON -DENABLE_MANUAL=OFF .. && \
    make -j8 && \
    make install && \
    ldconfig

# Set up the working directory
WORKDIR /app



# Copy application code
COPY . .

# Default command to run the application
CMD ["python", "app.py"]
