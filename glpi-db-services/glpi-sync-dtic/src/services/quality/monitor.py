"""
GLPI Quality Monitoring Service
Automated detection of GLPI ticket misuse
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import logging

from .rules import QUALITY_RULES

logger = logging.getLogger(__name__)


class QualityMonitor:
    """Main quality monitoring service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_all_checks(self) -> Dict[str, any]:
        """
        Execute all 5 quality rules and create alerts for violations.
        Returns summary of execution.
        """
        logger.info("Starting quality monitoring checks...")
        
        results = {
            'executed_at': datetime.utcnow().isoformat(),
            'rules_executed': 0,
            'alerts_created': 0,
            'violations_found': {},
            'errors': []
        }
        
        for rule_id, rule_config in QUALITY_RULES.items():
            try:
                violations = self.execute_rule(rule_id, rule_config)
                results['rules_executed'] += 1
                results['violations_found'][rule_id] = len(violations)
                
                # Only create alert if threshold exceeded
                if len(violations) > rule_config.get('threshold', 0):
                    alert_id = self.create_alert(rule_id, violations, rule_config)
                    results['alerts_created'] += 1
                    logger.info(f"Alert created for {rule_id}: {len(violations)} violations")
                else:
                    logger.debug(f"Rule {rule_id}: {len(violations)} violations (below threshold)")
                    
            except Exception as e:
                error_msg = f"Error executing rule {rule_id}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        logger.info(f"Quality checks completed: {results['alerts_created']} alerts created")
        return results
    
    def execute_rule(self, rule_id: str, config: Dict) -> List[Dict]:
        """Execute SQL query for a specific rule."""
        try:
            result = self.db.execute(text(config['query']))
            violations = [dict(row._mapping) for row in result]
            return violations
        except Exception as e:
            logger.error(f"Error executing query for {rule_id}: {str(e)}")
            raise
    
    def create_alert(
        self, 
        rule_id: str, 
        violations: List[Dict], 
        config: Dict
    ) -> Optional[int]:
        """
        Create or update alert in database.
        Returns alert ID.
        """
        try:
            # Check if alert already exists for this rule
            check_query = text("""
                SELECT id FROM dtic.quality_alerts
                WHERE rule_id = :rule_id
                  AND resolved_at IS NULL
                ORDER BY detected_at DESC
                LIMIT 1
            """)
            existing = self.db.execute(check_query, {'rule_id': rule_id}).fetchone()
            
            if existing:
                # Update existing alert metadata
                update_query = text("""
                    UPDATE dtic.quality_alerts
                    SET metadata = :metadata,
                        detected_at = NOW()
                    WHERE id = :alert_id
                    RETURNING id
                """)
                result = self.db.execute(update_query, {
                    'alert_id': existing[0],
                    'metadata': {
                        'total_violations': len(violations),
                        'violations': violations[:10],  # Store max 10 samples
                        'last_updated': datetime.utcnow().isoformat()
                    }
                })
                alert_id = existing[0]
                logger.info(f"Updated existing alert {alert_id} for {rule_id}")
            else:
                # Create new alert
                insert_query = text("""
                    INSERT INTO dtic.quality_alerts 
                    (rule_id, severity, ticket_id, metadata)
                    VALUES (:rule_id, :severity, :ticket_id, :metadata)
                    RETURNING id
                """)
                result = self.db.execute(insert_query, {
                    'rule_id': rule_id,
                    'severity': config['severity'],
                    'ticket_id': violations[0]['id'] if violations else None,
                    'metadata': {
                        'total_violations': len(violations),
                        'violations': violations[:10],
                        'rule_name': config['name'],
                        'description': config['description'],
                        'action': config['action']
                    }
                })
                alert_id = result.fetchone()[0]
                logger.info(f"Created new alert {alert_id} for {rule_id}")
            
            # Log dashboard notification
            self._log_notification(alert_id, 'dashboard')
            
            self.db.commit()
            return alert_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating alert for {rule_id}: {str(e)}")
            raise
    
    def _log_notification(self, alert_id: int, channel: str):
        """Log notification in alert_notifications table."""
        try:
            insert_query = text("""
                INSERT INTO dtic.alert_notifications (alert_id, channel, success)
                VALUES (:alert_id, :channel, TRUE)
            """)
            self.db.execute(insert_query, {
                'alert_id': alert_id,
                'channel': channel
            })
        except Exception as e:
            logger.warning(f"Failed to log notification: {str(e)}")
    
    def resolve_alert(self, alert_id: int, user_id: Optional[int] = None):
        """Mark alert as resolved."""
        try:
            update_query = text("""
                UPDATE dtic.quality_alerts
                SET resolved_at = NOW(),
                    resolved_by = :user_id
                WHERE id = :alert_id
            """)
            self.db.execute(update_query, {
                'alert_id': alert_id,
                'user_id': user_id
            })
            self.db.commit()
            logger.info(f"Alert {alert_id} resolved by user {user_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resolving alert {alert_id}: {str(e)}")
            raise
