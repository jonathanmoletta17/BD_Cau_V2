import time
import signal
import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.simple_agent import SimpleAgent

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [SERVICE] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GLPIService")

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True

def main():
    logger.info("Starting GLPI Ticket Classification Service...")
    
    try:
        agent = SimpleAgent()
    except Exception as e:
        logger.critical(f"Failed to initialize Agent: {e}")
        sys.exit(1)
        
    killer = GracefulKiller()
    
    logger.info("Service Loop Started. Polling every 60 seconds.")
    
    while not killer.kill_now:
        try:
            logger.info("Checking for new tickets...")
            agent.run_batch(limit=10)
        except Exception as e:
            logger.error(f"Error in batch execution: {e}")
        
        # Sleep loop to allow quicker interrupt handling
        for _ in range(60):
            if killer.kill_now:
                break
            time.sleep(1)
            
    logger.info("Service stopping gracefully.")

if __name__ == "__main__":
    main()
