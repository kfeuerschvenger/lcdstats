# Dockerfile
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    iputils-ping \
    procps \
    bc \
    libgpiod-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (without periphery/spidev for Docker)
RUN pip install --no-cache-dir \
    Pillow==10.3.0 \
    numpy==1.26.4 \
    python-periphery==2.4.1

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY_MODE=esp32

# Run the application
CMD ["python", "stats.py", "--display", "esp32", "--esp32-host", "192.168.0.199"]