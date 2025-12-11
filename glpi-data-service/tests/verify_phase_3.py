"""
Verification Script - Phase 3: Automation (Mocked)
Tests scripts/daemon_sync.py loop logic.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from daemon_sync import main, GracefulKiller

class TestDaemonSync(unittest.TestCase):
    
    @patch('daemon_sync.run_sync')
    @patch('daemon_sync.time')
    def test_daemon_loop(self, mock_time, mock_run_sync):
        """Test Daemon Loop Runs and Stops"""
        
        # Setup: Run once then stop
        # Method: side_effect on sleep to raise KeyboardInterrupt or modify kill_now?
        # Better: mock GracefulKiller to return kill_now=False once, then True
        
        # Actually, let's patch the GracefulKiller instance
        # or patch time.sleep to set kill_now = True via a side effect
        
        def set_kill(*args, **kwargs):
            # Find the killer instance? Hard to access local var.
            # But the loop checks killer.kill_now.
            # Alternatively, make time.sleep raise SystemExit?
            # Or make logic break.
            pass

        # Since we can't easily access local variable 'killer' inside main,
        # we can patch GracefulKiller class to return a mock that we control.
        
        with patch('daemon_sync.GracefulKiller') as MockKiller:
            instance = MockKiller.return_value
            # kill_now sequence: False (start), True (after 1 loop)
            # Property mock?
            type(instance).kill_now = unittest.mock.PropertyMock(side_effect=[False, True, True])
            
            # Run main
            main()
            
            # Verify run_sync called for DTIC and SIS
            self.assertTrue(mock_run_sync.called)
            self.assertEqual(mock_run_sync.call_count, 2) # Once for DTIC, Once for SIS
            
            # Verify Logs (implied by execution reaching end)
            print("\n✅ Daemon: Loop logic and graceful exit verified.")

if __name__ == '__main__':
    unittest.main()
