FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed
# (None strictly needed for pure python wheels, but usually good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
