# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# ffmpeg is required for audio resampling
# libsox-dev is required for some audio features
# build-essential is required for compiling webrtcvad
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsox-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure data directories exist (though they will usually be mounted)
RUN mkdir -p uploads models

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Default command (will be overridden in docker-compose for the worker)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
