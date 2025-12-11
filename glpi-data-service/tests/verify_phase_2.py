"""
Verification Script - Phase 2: CLI Integration (Mocked)
Tests scripts/sync.py logic flow.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import run_sync from scripts.sync
# We need to add scripts to path or import by file path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from sync import run_sync

class TestSyncCLI(unittest.TestCase):
    
    @patch('sync.SyncService')
    @patch('sync.GLPIClient')
    @patch('sync.Database')
    @patch('sync.Config')
    def test_run_sync_incremental_no_limit(self, mock_config, mock_db, mock_client, mock_service):
        """Test Incremental Run WITHOUT limit -> Should Update State"""
        
        # Setup Mock DB Session
        mock_session = MagicMock()
        mock_db.get_session.return_value = mock_session
        
        # Mock SyncState Query
        mock_state_ticket = MagicMock()
        mock_state_ticket.last_sync = datetime(2024, 1, 1)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_state_ticket
        
        # Run
        run_sync(context='dtic', sync_type='tickets', limit=None, incremental=True)
        
        # Check SyncService called with correct Date
        mock_service.sync_tickets.assert_called()
        args, kwargs = mock_service.sync_tickets.call_args
        self.assertEqual(kwargs.get('since_date'), datetime(2024, 1, 1))
        
        # Check State Updated
        # Since mock_state_ticket was returned, we check if its last_sync was updated
        # It should be updated to a new datetime (close to now)
        self.assertNotEqual(mock_state_ticket.last_sync, datetime(2024, 1, 1))
        
        # Check Commit called
        mock_session.commit.assert_called()
        print("\n✅ CLI: Incremental + No Limit -> State Updated correctly.")

    @patch('sync.SyncService')
    @patch('sync.GLPIClient')
    @patch('sync.Database')
    @patch('sync.Config')
    def test_run_sync_incremental_with_limit(self, mock_config, mock_db, mock_client, mock_service):
        """Test Incremental Run WITH limit -> Should NOT Update State"""
        
        mock_session = MagicMock()
        mock_db.get_session.return_value = mock_session
        
        mock_state_ticket = MagicMock()
        mock_state_ticket.last_sync = datetime(2024, 1, 1)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_state_ticket
        
        # Run
        run_sync(context='dtic', sync_type='tickets', limit=10, incremental=True)
        
        # Check SyncService called with correct Date
        args, kwargs = mock_service.sync_tickets.call_args
        self.assertEqual(kwargs.get('since_date'), datetime(2024, 1, 1))
        
        # Check State NOT Updated
        self.assertEqual(mock_state_ticket.last_sync, datetime(2024, 1, 1))
        
        # Check Commit NOT called (except for other commits? No, session is mocked)
        # Actually sync_tickets might commit internal batches, but run_sync commits state.
        # We assert that run_sync didn't commit state.
        # To be precise, we check if SyncState().last_sync = ... was executed?
        # But we reused the mock object.
        print("\n✅ CLI: Incremental + Limit -> State PROTECTED.")

if __name__ == '__main__':
    unittest.main()
