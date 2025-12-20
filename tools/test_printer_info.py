import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add tools to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import get_printer_info

class TestPrinterDiagnostics(unittest.TestCase):
    
    def setUp(self):
        # Basic server success response
        self.server_success = ({"Ping": True, "SMB": True}, None)
        self.server_fail = ({"Ping": False, "SMB": False}, None)

    @patch('get_printer_info.run_powershell_json')
    def test_no_printers(self, mock_run):
        """Test scenario where no printers are installed."""
        # First call: printers (empty list), Second call: server (success)
        mock_run.side_effect = [
            ([], None), 
            self.server_success
        ]
        
        info = get_printer_info.get_printer_diagnostics()
        
        self.assertEqual(len(info['printers']), 0)
        # Should detect no printers installed issue
        self.assertTrue(any("No printers installed" in i for i in info['issues']))

    @patch('get_printer_info.run_powershell_json')
    def test_printer_offline(self, mock_run):
        """Test scenario with an offline printer."""
        printer_mock = [{
            "Name": "Office Printer",
            "DriverName": "HP Universal",
            "PortName": "IP_192.168.1.100",
            "Shared": False,
            "Published": False,
            "DeviceType": "Print",
            "Status": "Offline", # Simulating Offline status
            "JobCount": 0,
            "IsDefault": True,
            "IsNetwork": False,
            "Server": None,
            "Location": "Office"
        }]
        
        mock_run.side_effect = [
            (printer_mock, None),
            self.server_success
        ]
        
        info = get_printer_info.get_printer_diagnostics()
        self.assertEqual(len(info['printers']), 1)
        # Check if offline issue is detected
        self.assertTrue(any("OFFLINE" in i for i in info['issues']))
        self.assertTrue(any("Check power" in s for s in info['suggestions']))

    @patch('get_printer_info.run_powershell_json')
    def test_printer_error_state(self, mock_run):
        """Test scenario with a printer in Error state."""
        printer_mock = [{
            "Name": "Broken Printer",
            "DriverName": "Generic",
            "PortName": "USB001",
            "Shared": False,
            "Published": False,
            "DeviceType": "Print",
            "Status": "Error", 
            "JobCount": 0,
            "IsDefault": True,
            "IsNetwork": False,
            "Server": None,
            "Location": ""
        }]
        
        mock_run.side_effect = [
            (printer_mock, None),
            self.server_success
        ]
        
        info = get_printer_info.get_printer_diagnostics()
        self.assertTrue(any("ERROR state" in i for i in info['issues']))

    @patch('get_printer_info.run_powershell_json')
    def test_high_queue_count(self, mock_run):
        """Test scenario with high job count."""
        printer_mock = [{
            "Name": "Busy Printer",
            "DriverName": "Generic",
            "PortName": "USB001",
            "Shared": False,
            "Published": False,
            "DeviceType": "Print",
            "Status": "Normal", 
            "JobCount": 10, # High count
            "IsDefault": True,
            "IsNetwork": False,
            "Server": None,
            "Location": ""
        }]
        
        mock_run.side_effect = [
            (printer_mock, None),
            self.server_success
        ]
        
        info = get_printer_info.get_printer_diagnostics()
        self.assertTrue(any("High queue count" in i for i in info['issues']))

    @patch('get_printer_info.run_powershell_json')
    def test_server_unreachable_with_mapped_printers(self, mock_run):
        """Test scenario where server is down but printers are mapped."""
        printer_mock = [{
            "Name": "\\\\piratinipaeps02\\SharedPrinter",
            "DriverName": "Driver",
            "PortName": "Port",
            "Shared": False,
            "Published": False,
            "DeviceType": "Print",
            "Status": "Normal",
            "JobCount": 0,
            "IsDefault": True,
            "IsNetwork": True,
            "Server": "piratinipaeps02",
            "Location": ""
        }]
        
        mock_run.side_effect = [
            (printer_mock, None),
            self.server_fail
        ]
        
        info = get_printer_info.get_printer_diagnostics()
        self.assertFalse(info['server_integration']['accessible'])
        self.assertTrue(any("unreachable" in i for i in info['issues']))
        self.assertTrue(any("mapped from piratinipaeps02 but server unreachable" in i for i in info['issues']))

if __name__ == '__main__':
    unittest.main()
