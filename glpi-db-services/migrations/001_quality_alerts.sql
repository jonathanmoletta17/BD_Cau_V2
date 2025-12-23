-- =====================================================
-- GLPI Quality Monitoring System - Database Schema
-- Phase 2: Top 5 Alert Rules
-- =====================================================

-- Create quality_alerts table
CREATE TABLE IF NOT EXISTS dtic.quality_alerts (
    id SERIAL PRIMARY KEY,
    alert_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    rule_id VARCHAR(10) NOT NULL,
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW')),
    ticket_id INTEGER REFERENCES dtic.tickets(id),
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP NULL,
    resolved_by INTEGER REFERENCES dtic.glpi_users(id),
    metadata JSONB,
    
    -- Indexes
    CONSTRAINT chk_severity CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW'))
);

CREATE INDEX idx_quality_alerts_rule ON dtic.quality_alerts(rule_id);
CREATE INDEX idx_quality_alerts_severity ON dtic.quality_alerts(severity);
CREATE INDEX idx_quality_alerts_detected ON dtic.quality_alerts(detected_at DESC);
CREATE INDEX idx_quality_alerts_ticket ON dtic.quality_alerts(ticket_id);
CREATE INDEX idx_quality_alerts_active ON dtic.quality_alerts(resolved_at) WHERE resolved_at IS NULL;

-- Create alert_notifications table
CREATE TABLE IF NOT EXISTS dtic.alert_notifications (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER NOT NULL REFERENCES dtic.quality_alerts(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

CREATE INDEX idx_alert_notifications_alert ON dtic.alert_notifications(alert_id);
CREATE INDEX idx_alert_notifications_channel ON dtic.alert_notifications(channel);

-- Create view for active alerts with ticket info
CREATE OR REPLACE VIEW dtic.active_alerts AS
SELECT 
    a.id,
    a.alert_uuid,
    a.rule_id,
    a.severity,
    a.ticket_id,
    a.detected_at,
    a.metadata,
    t.glpi_id,
    t.titulo,
    t.status_id,
    COALESCE(u_tech.name, 'Sem Técnico') as tecnico,
    COALESCE(g.name, 'Sem Grupo') as grupo,
    COUNT(n.id) as notification_count
FROM dtic.quality_alerts a
LEFT JOIN dtic.tickets t ON a.ticket_id = t.id
LEFT JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
LEFT JOIN dtic.glpi_users u_tech ON tu.user_id = u_tech.id
LEFT JOIN dtic.tickets_groups tg ON t.id = tg.ticket_id AND tg.type = 2
LEFT JOIN dtic.glpi_groups g ON tg.group_id = g.id
LEFT JOIN dtic.alert_notifications n ON a.id = n.alert_id
WHERE a.resolved_at IS NULL
GROUP BY a.id, a.alert_uuid, a.rule_id, a.severity, a.ticket_id, 
         a.detected_at, a.metadata, t.glpi_id, t.titulo, t.status_id, 
         u_tech.name, g.name;

-- Create aggregated summary view
CREATE OR REPLACE VIEW dtic.quality_summary AS
SELECT 
    rule_id,
    severity,
    COUNT(*) as total_alerts,
    COUNT(DISTINCT ticket_id) as affected_tickets,
    MAX(detected_at) as last_detected
FROM dtic.quality_alerts
WHERE resolved_at IS NULL
GROUP BY rule_id, severity
ORDER BY 
    CASE severity 
        WHEN 'HIGH' THEN 1 
        WHEN 'MEDIUM' THEN 2 
        WHEN 'LOW' THEN 3 
    END,
    total_alerts DESC;

-- Grant permissions (adjust user as needed)
GRANT SELECT, INSERT, UPDATE ON dtic.quality_alerts TO glpi_user;
GRANT SELECT, INSERT ON dtic.alert_notifications TO glpi_user;
GRANT SELECT ON dtic.active_alerts TO glpi_user;
GRANT SELECT ON dtic.quality_summary TO glpi_user;
GRANT USAGE, SELECT ON SEQUENCE dtic.quality_alerts_id_seq TO glpi_user;
GRANT USAGE, SELECT ON SEQUENCE dtic.alert_notifications_id_seq TO glpi_user;

-- Insert sample comment for documentation
COMMENT ON TABLE dtic.quality_alerts IS 'Stores quality alerts for GLPI ticket misuse detection';
COMMENT ON TABLE dtic.alert_notifications IS 'Logs all notifications sent for quality alerts';
COMMENT ON VIEW dtic.active_alerts IS 'Active alerts enriched with ticket and user information';
COMMENT ON VIEW dtic.quality_summary IS 'Aggregated summary of active alerts by rule and severity';
