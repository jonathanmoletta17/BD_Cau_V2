import sys
from pathlib import Path

# Add services/common to path
sys.path.insert(0, str(Path(__file__).parent / 'services/common'))

def test_imports():
    print("Testing Imports...")
    try:
        from src.core.config import config
        print(f"✅ Config loaded. DB URL: {config.DATABASE_URL[:20]}...")
        
        from src.core.database import Database
        print("✅ Database class imported.")
        
        from src.core.glpi_client import GLPIClient
        print("✅ GLPIClient class imported.")
        
        print("\nAll systems go! Common library is functional.")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
