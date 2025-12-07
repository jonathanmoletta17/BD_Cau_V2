"""
Full Database Rebuild
Complete cycle: DROP → CREATE → SYNC
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime


# Determine script directory
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def run_script(script_name, description, auto_confirm=None):
    """Run a script with optional auto-confirmation."""
    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)
    
    start = datetime.now()
    
    # Use absolute path to script
    script_path = SCRIPT_DIR / script_name
    
    try:
        if auto_confirm:
            # Pipe confirmation to script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                input=auto_confirm,
                capture_output=True,
                text=True,
                timeout=600,
                encoding='utf-8',
                errors='replace',
                cwd=str(PROJECT_ROOT)
            )
        else:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=600,
                encoding='utf-8',
                errors='replace',
                cwd=str(PROJECT_ROOT)
            )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"\n❌ ERROR in {description}")
            if result.stderr:
                print(result.stderr)
            return False
        
        duration = (datetime.now() - start).total_seconds()
        print(f"✅ Completed in {duration:.1f}s")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Full database rebuild cycle."""
    print("\n" + "=" * 70)
    print("🔄 FULL DATABASE REBUILD")
    print(f"Started: {datetime.now()}")
    print("=" * 70)
    
    response = input("\n⚠️  This will DESTROY and RECREATE the entire database.\nType 'REBUILD' to confirm: ")
    if response != "REBUILD":
        print("❌ Cancelled")
        return
    
    overall_start = datetime.now()
    
    # Step 1: Drop tables
    if not run_script("drop_tables.py", "Drop All Tables", "DROP TABLES\n"):
        print("\n❌ REBUILD FAILED")
        sys.exit(1)
    
    # Step 2: Create tables
    if not run_script("create_tables.py", "Create All Tables"):
        print("\n❌ REBUILD FAILED")
        sys.exit(1)
    
    # Step 3: Sync all data
    if not run_script("sync_all.py", "Sync All Data"):
        print("\n[ERROR] REBUILD FAILED")
        sys.exit(1)
    
    # Summary
    total_duration = (datetime.now() - overall_start).total_seconds()
    print("\n" + "=" * 70)
    print("✅ DATABASE REBUILD COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Total time: {total_duration / 60:.1f} minutes")
    print(f"Finished: {datetime.now()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
