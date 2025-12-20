import sys
import os
import asyncio

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from agents.local_triage.services_factory import get_classifier

async def test_engine_loading():
    print("--- Testing Engine Transplant ---")
    try:
        classifier = get_classifier()
        print(f"✅ Engine Instance: {classifier}")
        print(f"✅ Categories Cached: {len(classifier.categories_cache)}")
        
        # Verify it loaded the 160 categories
        if len(classifier.categories_cache) > 100:
            print("SUCCESS: Engine has full knowledge base!")
        else:
            print("WARNING: Engine loaded but seems empty. Check paths.")
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_engine_loading())
