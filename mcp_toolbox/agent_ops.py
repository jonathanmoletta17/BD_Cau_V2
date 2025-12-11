import subprocess
import json
import os

SCRIPT_LOCAL_PATH = "mcp_toolbox/predict_wrapper.py"
CONTAINER_TARGET_PATH = "/app/tools/predict_wrapper.py" # Assuming /app is WORKDIR

def deploy_wrapper():
    """Copies the wrapper script to the container."""
    try:
        # Check if local file exists
        if not os.path.exists(SCRIPT_LOCAL_PATH):
            return False, "Local wrapper file not found"
            
        cmd = ["docker", "cp", SCRIPT_LOCAL_PATH, f"agent-ticket-web:{CONTAINER_TARGET_PATH}"]
        subprocess.run(cmd, check=True)
        return True, "Context deployed"
    except Exception as e:
        return False, str(e)

def simulate_classification(title, description):
    """
    Runs the prediction wrapper inside the container.
    """
    # Ensure wrapper is there (lazy deployment)
    ok, msg = deploy_wrapper()
    if not ok:
        return {"error": f"Deployment failed: {msg}"}
        
    cmd = [
        "docker", "exec", "agent-ticket-web",
        "python", "tools/predict_wrapper.py",
        title, description
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean output (ignore logs if any mixed in stdout - wrapper should output clean JSON on print)
        # But SimpleAgent init logs to stdout... we configured handler to stdout.
        # This is a problem. The wrapper output will be mixed with "Initializing Simple Agent..." logs.
        # We need to parse the LAST line or filter for JSON.
        
        lines = result.stdout.strip().split('\n')
        json_line = ""
        for line in lines:
            if line.startswith("{"):
                json_line = line
                break
        
        if not json_line:
            # Try last line
            json_line = lines[-1] if lines else ""

        try:
             return json.loads(json_line)
        except:
             return {"error": "Failed to parse JSON", "raw_output": result.stdout}

    except Exception as e:
        return {"error": f"Execution failed: {e}"}
