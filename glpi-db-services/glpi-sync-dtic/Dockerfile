FROM python:3.10-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Common Dependencies (if any special ones, but we assume requirements.txt has everything)
# Copy Service Requirements
COPY glpi-db-services/glpi-sync-dtic/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Common Library
COPY glpi-db-services/common /app/services/common

# Copy Service Code
COPY glpi-db-services/glpi-sync-dtic /app/services/glpi-sync-dtic

# Set PYTHONPATH to include common and the service
ENV PYTHONPATH="${PYTHONPATH}:/app/services/common:/app/services/glpi-sync-dtic"

# Set Working Directory to Service
WORKDIR /app/services/glpi-sync-dtic

# Run Daemon
CMD ["python", "scripts/daemon_sync.py"]
