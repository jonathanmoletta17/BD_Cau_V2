# Use NVIDIA's PyTorch image as base (includes CUDA/cuDNN)
FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /app

# Install system dependencies if any (usually clean in this image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for cache optimization
# Assuming requirements.txt exists in root; if not, we create minimal one
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
# Explicitly install sentence-transformers as it might not be in base
# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app

# Set Environment Variables
ENV ENVIRONMENT=test
# PYTHONUNBUFFERED ensures logs show up immediately
ENV PYTHONUNBUFFERED=1 

# Command to run the service
CMD ["python", "-u", "tools/run_service.py"]
