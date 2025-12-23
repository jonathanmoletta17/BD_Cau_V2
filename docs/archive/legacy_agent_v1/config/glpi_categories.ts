export const GLPI_CATEGORIES = {
    CREATE_USER: 35,       // 'ACESSO A SISTEMAS > REDE > LIBERAÇÃO DE ACESSO > NOVO USUÁRIO'
    PRINTER_ISSUE: 14,     // 'IMPRESSORA' (Generic parent, safe default)
    RESET_PASSWORD: 24,    // 'ACESSO A SISTEMAS > REDE > RESET DE SENHA'
    PRINTER_TONER: 71,     // 'IMPRESSORA > TROCA DE TONNER'
    DEFAULT: 7             // 'AJUDA E SUPORTE'
};

/**
 * Maps Internal Intents to GLPI Category IDs
 */
export function getCategoryId(intent: string, payload?: any): number {
    switch (intent) {
        case 'create_user': return GLPI_CATEGORIES.CREATE_USER;
        case 'printer_issue':
            if (payload?.issue_type === 'Toner') return GLPI_CATEGORIES.PRINTER_TONER;
            return GLPI_CATEGORIES.PRINTER_ISSUE;
        case 'reset_password': return GLPI_CATEGORIES.RESET_PASSWORD;
        default: return GLPI_CATEGORIES.DEFAULT;
    }
}
