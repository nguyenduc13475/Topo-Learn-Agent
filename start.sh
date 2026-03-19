#!/bin/bash
set -e

echo "🔍 Checking for NVIDIA GPU..."

if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected. Booting with CUDA..."

    rm -f backend/worker.cpu.Dockerfile docker-compose.override.yml

    docker compose --env-file backend/.env up --build
else
    echo "⚠️ No GPU detected. Using CPU mode..."

    # Dynamically generate the CPU-only Dockerfile
    cat << 'EOF' > backend/worker.cpu.Dockerfile
FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y ca-certificates ffmpeg libsm6 libxext6 libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"
RUN python -c "from docling.document_converter import DocumentConverter; DocumentConverter()"
COPY . .
CMD ["celery", "-A", "app.core.celery_app", "worker", "--loglevel=info", "-c", "2"]
EOF

    # Dynamically generate the docker-compose override
    cat << 'EOF' > docker-compose.override.yml
services:
  worker:
    build:
      context: ./backend
      dockerfile: worker.cpu.Dockerfile
    deploy:
      resources:
        reservations:
          devices: []
EOF

    echo "✅ CPU configurations generated. Starting containers..."
    docker compose --env-file backend/.env up --build
fi