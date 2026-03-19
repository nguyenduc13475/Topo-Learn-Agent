# backend/Dockerfile
FROM python:3.10-slim

# Set environment variables for non-interactive installs and Python behavior
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies drastically reduced as AI processing is offloaded to Gemini API
RUN apt-get update && apt-get install -y \
    ca-certificates ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and run server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]