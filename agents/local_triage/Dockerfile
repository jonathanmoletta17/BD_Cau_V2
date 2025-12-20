FROM python:3.10-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Common Python Dependencies
# We install Agent A's deps first (Base) then Agent B's (Graph features)
# Assuming context is Repo Root, so paths are relative to Root

COPY agents/triage/requirements.txt /tmp/req_a.txt
COPY agents/local_triage/requirements.txt /tmp/req_b.txt

RUN pip install --no-cache-dir -r /tmp/req_a.txt
RUN pip install --no-cache-dir -r /tmp/req_b.txt

# Copy ENTIRE Monorepo to allow cross-imports (src.services...)
COPY . /app

# Expose Chainlit Port
EXPOSE 8000

# Default Command (Overridden in Compose, but safe default)
CMD ["chainlit", "run", "agents/local_triage/ui.py", "--host", "0.0.0.0", "--port", "8000", "--headless"]
