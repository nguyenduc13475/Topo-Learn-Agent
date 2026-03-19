# Use NVIDIA CUDA base image for GPU acceleration
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python 3.10 and required system libraries for OpenCV and Docling
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-distutils python3-pip \
    ca-certificates ffmpeg libsm6 libxext6 libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Alias python3 to python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Install PyTorch with CUDA 11.8 support FIRST to ensure GPU usage
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install the rest of the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# CRITICAL: PRE-DOWNLOAD ML MODELS
# ==========================================
# Force download of Whisper and Docling models into the Docker image layer.
# This ensures the worker is instantly ready to process files without runtime downloading.
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"
RUN python -c "from docling.document_converter import DocumentConverter; DocumentConverter()"

COPY . .

# Run Celery Worker
CMD ["celery", "-A", "app.core.celery_app", "worker", "--loglevel=info", "-c", "4"]