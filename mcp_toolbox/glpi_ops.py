import subprocess
import json

def trigger_sync(context="all", sync_type="tickets"):
    """
    Triggers the sync process inside the glpi-data-service container.
    """
    cmd = [
        "docker", "exec", "glpi-data-service",
        "python", "scripts/sync.py",
        "--context", context,
        "--type", sync_type,
        "--limit", "5" # Defaulting to small limit for safety/testing
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        }

def check_sync_status():
    """
    Checks the logs of the service to see if sync ran recently.
    """
    cmd = ["docker", "logs", "--tail", "50", "glpi-data-service"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error reading logs: {e}"
