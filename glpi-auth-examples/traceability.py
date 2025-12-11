import logging
import json
from datetime import datetime
import os

class TraceabilityLogger:
    def __init__(self, log_file="auth_trace.jsonl"):
        self.log_file = log_file
        # Ensure log directory exists if path has directories
        if os.path.dirname(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
        # Configure logging
        self.logger = logging.getLogger("TraceabilityLogger")
        self.logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if initialized multiple times
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            self.logger.addHandler(console_handler)

    def log_action(self, user_id, action, details=None, status="success"):
        """
        Registra uma ação do usuário para auditoria.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "status": status,
            "details": details or {}
        }
        self.logger.info(json.dumps(entry))
        return entry

if __name__ == "__main__":
    # Teste rápido
    tracer = TraceabilityLogger("scripts/auth_examples/logs/audit.jsonl")
    tracer.log_action("user123", "login", {"method": "glpi_api"})
    tracer.log_action("user123", "create_ticket", {"ticket_id": 100})
