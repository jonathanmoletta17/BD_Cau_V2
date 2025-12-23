FROM python:3.10-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY glpi-services/glpi-sync-sis/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Common Library
COPY glpi-services/common /app/services/common

# Copy Service Code
COPY glpi-services/glpi-sync-sis /app/services/glpi-sync-sis

# Set PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/services/common:/app/services/glpi-sync-sis"

# Set Working Directory
WORKDIR /app/services/glpi-sync-sis

# Run Daemon
CMD ["python", "scripts/daemon_sync.py"]
