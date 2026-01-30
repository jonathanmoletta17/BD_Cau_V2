"""
Daemon Sync Script
Runs incremental sync in a continuous loop.
"""
import sys
import time
import logging
import signal
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import run_sync from scripts.sync
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from sync import run_sync

# Import Database & SyncState for bootstrap checks
from src.core import Database
from src.core.models import SyncState
from src.core.models import BootstrapState
from sqlalchemy import text # Fix: Import text for raw sql execution if needed, or just use ORM query

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DAEMON - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("daemon.log")
    ]
)
logger = logging.getLogger(__name__)

LOOP_INTERVAL = 10 # Seconds

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

def wait_for_db(max_retries=60, sleep_sec=2):
    """Wait for database to be ready."""
    logger.info("⏳ Waiting for Database...")
    for i in range(max_retries):
        try:
            # Try to get a session
            session = Database.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            logger.info("✅ Database is Ready!")
            return True
        except Exception:
            if i % 5 == 0:
                logger.info(f"   Waiting for DB... ({i+1}/{max_retries})")
            time.sleep(sleep_sec)
    return False

def ensure_schema():
    """Run create_db logic effectively."""
    logger.info("🛠️ Ensuring Database Schema...")
    try:
        # We can import and run the create_db main, or just rely on models being imported
        # and calling create_all via Database.engine
        
        # Simpler: Import the models and call create_all directly if we have the reference
        # But create_db.py does it well. Let's call it via subprocess or import ??
        # Importing main from create_db might be tricky if it doesn't have a main() function nicely exposed 
        # (It has `if __name__ == '__main__':`)
        # Better: Use src.core.database logic if available or just raw SQLAlchemy
        
        # Re-import All Models to ensure registration (like create_db.py does)
        # We need to make sure all modules are imported.
        # This is a bit heavy.
        # Alternative: Assume data-service container ALREADY runs create_db?
        # Dockerfile says: CMD uvicorn...
        # It does NOT run create_db automatically in CMD.
        # So we MUST do it here.
        
        # Let's use subprocess to run the existing verified script
        import subprocess
        script_path = Path(__file__).parent / 'create_db.py'
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Schema Verified/Created.")
        else:
            logger.error(f"❌ Schema Setup Failed: {result.stderr}")
            raise Exception("Schema Setup Failed")
            
    except Exception as e:
        logger.error(f"❌ Error ensuring schema: {e}")
        raise

def bootstrap_if_needed(contexts=['dtic', 'sis']):
    logger.info("🔎 Checking Bootstrap Status...")
    session = Database.get_session()
    pending = []
    try:
        for ctx in contexts:
            state = session.query(BootstrapState).filter_by(context=ctx).first()
            if not state or state.status != 'completed':
                pending.append(ctx)
    finally:
        session.close()

    if not pending:
        logger.info("✅ Bootstrap already completed.")
        return

    logger.info("🚀 Starting Full Bootstrap...")
    for ctx in pending:
        # 1. Mark as Pending
        session = Database.get_session()
        try:
            bs = session.query(BootstrapState).filter_by(context=ctx).first()
            if not bs:
                bs = BootstrapState(context=ctx, status='pending', last_attempt=datetime.utcnow())
                session.add(bs)
            else:
                bs.status = 'pending'
                bs.last_attempt = datetime.utcnow()
            session.commit()
        finally:
            session.close()

        logger.info(f"   Bootstrapping {ctx.upper()}...")
        try:
            # 2. Run Sync (It manages its own sessions)
            run_sync(context=ctx, sync_type='all', limit=None, incremental=False)
            
            # 3. Mark as Completed
            session = Database.get_session()
            try:
                bs = session.query(BootstrapState).filter_by(context=ctx).first()
                bs.status = 'completed'
                bs.last_attempt = datetime.utcnow()
                session.commit()
                logger.info(f"   {ctx.upper()} completed.")
            finally:
                session.close()

        except Exception as e:
            logger.error(f"❌ Bootstrap error on {ctx}: {e}")
            # Ensure it stays pending or logs error
            raise

def main():
    logger.info("🚀 Starting GLPI Sync Daemon...")
    killer = GracefulKiller()
    
    # 1. Wait for DB
    if not wait_for_db():
        logger.error("❌ DB not available. Exiting.")
        sys.exit(1)
        
    # 2. Ensure Schema
    ensure_schema()
    
    # 3. Bootstrap (Full Sync if empty)
    contexts = ['dtic', 'sis']
    bootstrap_if_needed(contexts)
    
    # 4. Loop
    logger.info(f"🔄 Entering Real-Time Loop (Interval: {LOOP_INTERVAL}s)")
    while not killer.kill_now:
        start_time = time.time()
        
        try:
            # Run Sequential or Parallel? 
            # Sync Logic handles parallelism internally if we call main() from sync.
            # But here we call run_sync directly.
            # Let's run sequentially per loop for safer debugging, or parallel if performance is needed.
            # sync.py uses ThreadPoolExecutor. We can do the same but let's keep it simple first.
            
            for ctx in contexts:
                logger.info(f"🔄 Tick: Syncing {ctx.upper()}...")
                run_sync(context=ctx, sync_type='metadata', incremental=True)
                run_sync(context=ctx, sync_type='tickets', incremental=True)
                
            elapsed = time.time() - start_time
            logger.info(f"✅ Tick Complete in {elapsed:.2f}s.")
            
        except MemoryError:
            logger.critical("❌ OUT OF MEMORY! Exiting to restart container.")
            sys.exit(137) # OOM exit code standard
        except Exception as e:
            logger.error(f"❌ Error in Sync Loop: {e}")
            import traceback
            traceback.print_exc()
        
        # Sleep
        if not killer.kill_now:
            logger.info(f"💤 Sleeping {LOOP_INTERVAL}s...")
            time.sleep(LOOP_INTERVAL)
    
    logger.info("🛑 Daemon Stopped Gracefully.")

if __name__ == "__main__":
    main()
