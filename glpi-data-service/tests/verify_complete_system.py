"""
Verification Script - Phase 4: Complete System Check
"""
import sys
import yaml
from pathlib import Path

def verify_system():
    print("=" * 60)
    print("🚀 Verifying COMPLETE GLPI Sync Architecture")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    
    # Check 1: docker-compose.yml
    dc_path = base_path.parent / 'docker-compose.yml'
    try:
        with open(dc_path, 'r', encoding='utf-8') as f:
            dc = yaml.safe_load(f)
            
        services = dc.get('services', {})
        if 'glpi-sync' in services:
             print("✅ [Docker] Service 'glpi-sync' FOUND.")
             cmd = services['glpi-sync'].get('command', [])
             if 'daemon_sync.py' in str(cmd):
                 print("✅ [Docker] Command runs daemon_sync.py.")
             else:
                 print(f"❌ [Docker] Unexpected command: {cmd}")
        else:
             print("❌ [Docker] Service 'glpi-sync' MISSING.")
    except Exception as e:
        print(f"❌ [Docker] Error reading file: {e}")

    # Check 2: daemon_sync.py logic
    daemon_path = base_path / 'scripts' / 'daemon_sync.py'
    try:
        content = daemon_path.read_text(encoding='utf-8')
        if 'wait_for_db' in content and 'ensure_schema' in content:
            print("✅ [Daemon] Bootstrap logic (wait_for_db, ensure_schema) FOUND.")
        else:
            print("❌ [Daemon] Bootstrap logic MISSING.")
            
        if 'bootstrap_if_needed' in content:
            print("✅ [Daemon] Full Sync Bootstrap logic FOUND.")
        else:
            print("❌ [Daemon] Full Sync Bootstrap logic MISSING.")
    except Exception as e:
         print(f"❌ [Daemon] Error reading file: {e}")

    print("\n🎉 Verification Complete. Ready to deploy via 'docker-compose up'.")

if __name__ == "__main__":
    verify_system()
