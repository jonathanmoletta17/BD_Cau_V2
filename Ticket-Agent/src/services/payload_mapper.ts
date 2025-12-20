import { GLPI_CATEGORIES, getCategoryId } from "../agent/config/glpi_categories";

export interface GlpiTicketPayload {
    name: string;
    content: string;
    urgency: number;
    impact: number;
    priority?: number;
    itilcategories_id: number;
}

export class PayloadMapper {
    /**
     * Maps the Agent V2 JSON Payload to GLPI Ticket Parameters
     */
    static mapToTicket(intent: string, payload: any, categoryOverride?: number, systemInfo?: any): GlpiTicketPayload {
        const categoryId = categoryOverride || getCategoryId(intent);

        let title = `[IA] Ticket Automático: ${intent.toUpperCase()}`;
        let content = "<h3>Ticket Aberto por Agente IA</h3><ul>";
        let urgency = 3; // Medium by default

        // 1. Format Content (HTML List)
        for (const [key, value] of Object.entries(payload)) {
            content += `<li><b>${this.formatLabel(key)}:</b> ${value}</li>`;
        }
        content += "</ul>";

        // 2. Specific Logic per Intent
        if (intent === 'create_user') {
            title = `[Acesso] Novo Usuário: ${payload.full_name || 'Desconhecido'}`;
            content += "<p><i>Solicitação de criação validada conforme governança.</i></p>";
        } else if (intent === 'printer_issue') {
            title = `[Impressora] Problema: ${payload.description?.substring(0, 30)}...`;
            urgency = 4; // High for physical assets
        } else if (intent === 'reset_password') {
            title = `[Senha] Reset para: ${payload.username}`;
            content += "<p><b>ATENÇÃO:</b> Proceder com reset no AD/Sistema.</p>";
        }

        // 3. Append System Info (if provided)
        // 3. Append System Info (if provided) - User Request Simple Footer
        if (systemInfo) {
            const net = systemInfo.Network || {};
            const hw = systemInfo.Hardware || {};

            // Add separation
            content += "<br><br>";

            // Simple Footer Format
            // N/S: XXXXX
            // IP: X.X.X.X
            if (hw.SerialNumber) content += `N/S: ${hw.SerialNumber}<br>`;
            if (net.IP) content += `IP: ${net.IP}`;
        }

        const result: GlpiTicketPayload = {
            name: title,
            content: content,
            urgency: urgency,
            itilcategories_id: categoryId,
            impact: payload.impact ? parseInt(payload.impact) : 3,
            priority: 3
        };

        // Override urgency if provided in payload
        if (payload.urgency) {
            result.urgency = parseInt(payload.urgency);
        }

        return result;
    }

    private static formatLabel(key: string): string {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}
