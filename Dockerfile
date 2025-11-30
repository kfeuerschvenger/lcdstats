# Dockerfile
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    iputils-ping \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (without periphery/spidev for Docker)
RUN pip install --no-cache-dir \
    Pillow==10.3.0 \
    numpy==1.26.4

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY_MODE=esp32

# Run the application
CMD ["python", "stats.py"]