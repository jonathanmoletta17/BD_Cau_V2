"""
Verification Script - Phase 1: Logic Tests (Mocked)
Ensures parameters are correctly passed to GLPI options.
"""
import sys
import unittest
from unittest.mock import MagicMock
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.sync_service import SyncService

class TestSyncServicePhase1(unittest.TestCase):
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.make_request.return_value = [] # Return empty list so loop breaks immediately use result of _fetch_with_backoff which calls this
        
        # Mock Session and Models (dummies)
        self.mock_session = MagicMock()
        self.mock_ticket_model = MagicMock()
        self.mock_models = {'Ticket': MagicMock(), 'TicketChange': MagicMock()}
        
    def test_sync_tickets_with_date(self):
        """Verify that since_date adds date_mod criteria."""
        since_date = datetime(2025, 1, 1, 12, 0, 0)
        
        # Call Sync
        SyncService.sync_tickets(
            self.mock_client, 
            self.mock_session, 
            self.mock_ticket_model, 
            valid_ids={}, 
            since_date=since_date
        )
        
        # Check calls
        # We assume _fetch_with_backoff calls make_request with params
        # We assume _fetch_with_backoff logic: client.make_request(endpoint, params)
        # We need to check if 'criteria[0][field]' == 'date_mod' exists in some call params
        
        found_date_criteria = False
        for call in self.mock_client.make_request.call_args_list:
            args, kwargs = call
            params = args[1] if len(args) > 1 else kwargs.get('params', {})
            
            # Check for date_mod criterion
            # Note: The logic adds criteria keys like 'criteria[0][field]'
            if params.get('criteria[0][field]') == 'date_mod' and \
               params.get('criteria[0][value]') == '2025-01-01 12:00:00':
                found_date_criteria = True
                break
        
        self.assertTrue(found_date_criteria, "SyncTickets did NOT send date_mod criteria to GLPIClient.")
        print("\n✅ SyncTickets: Incremental criteria verified.")

    def test_sync_ticket_changes_with_date(self):
        """Verify that since_date adds date_mod criteria for Logs."""
        since_date = datetime(2025, 1, 1, 12, 0, 0)
        
        SyncService.sync_ticket_changes(
            self.mock_client,
            self.mock_session,
            self.mock_models,
            valid_ids={},
            since_date=since_date
        )
        
        # Criteria for logs is usually index 1 or appended
        found_date_criteria = False
        for call in self.mock_client.make_request.call_args_list:
            args, kwargs = call
            endpoint = args[0]
            if endpoint != 'Log': continue
            
            params = args[1] if len(args) > 1 else kwargs.get('params', {})
            
            # Implementation details:
            # SyncService adds:
            # criteria[1][field] = date_mod
            
            if params.get('criteria[1][field]') == 'date_mod' and \
               params.get('criteria[1][value]') == '2025-01-01 12:00:00':
                found_date_criteria = True
                break
                
        self.assertTrue(found_date_criteria, "SyncTicketChanges did NOT send date_mod criteria.")
        print("\n✅ SyncTicketChanges: Incremental criteria verified.")

if __name__ == '__main__':
    unittest.main()
