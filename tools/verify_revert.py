import sys
from pathlib import Path

# Setup path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

def verify():
    print("Checking imports...")
    try:
        from agents.triage.ui import auth_callback, on_action
        from agents.triage.src.services.glpi_client import GLPIClient
        
        # Inspect GLPIClient to ensure methods are gone
        client_attrs = dir(GLPIClient)
        if 'get_user_groups' in client_attrs:
             print("FAIL: get_user_groups still present in GLPIClient")
             sys.exit(1)
        if 'get_user_subordinates_count' in client_attrs:
             print("FAIL: get_user_subordinates_count still present in GLPIClient")
             sys.exit(1)
             
        print("PASS: Methods removed.")
        print("Imports successful.")
        
    except ImportError as e:
        print(f"Import Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
