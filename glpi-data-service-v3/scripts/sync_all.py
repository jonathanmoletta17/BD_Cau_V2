"""
Sync Orchestrator - V3
Executes all sync scripts in correct order
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime


# Determine script directory
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def run_sync(script_name, description):
    """Run a sync script and return success status."""
    print("=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)
    
    start = datetime.now()
    
    # Use absolute path to script
    script_path = SCRIPT_DIR / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes (increased for large initial sync)
            encoding='utf-8',
            errors='replace',
            cwd=str(PROJECT_ROOT)  # Run from project root
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"\n[ERROR] in {description}")
            if result.stderr:
                print(result.stderr)
            return False
        
        duration = (datetime.now() - start).total_seconds()
        print(f"\n[OK] Completed in {duration:.1f}s\n")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"\n[ERROR] TIMEOUT in {description}")
        return False
    except Exception as e:
        print(f"\n[ERROR] in {description}: {e}")
        return False


def main():
    """Run all syncs in order."""
    print("\n" + "=" * 70)
    print("GLPI DATA SERVICE V3 - FULL SYNCHRONIZATION")
    print(f"Started: {datetime.now()}")
    print("=" * 70)
    print()
    
    overall_start = datetime.now()
    
    # Sync steps in dependency order
    steps = [
        ("sync_metadata.py", "Metadata (Users, Groups, Entities, etc.)"),
        ("sync_tickets.py", "Tickets + Actors + Changes"),
    ]
    
    for script, description in steps:
        if not run_sync(script, description):
            print("\n" + "=" * 70)
            print("[ERROR] SYNC FAILED - Stopping")
            print("=" * 70)
            sys.exit(1)
    
    # Summary
    total_duration = (datetime.now() - overall_start).total_seconds()
    print("=" * 70)
    print("[OK] FULL SYNC COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Total time: {total_duration / 60:.1f} minutes")
    print(f"Finished: {datetime.now()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
