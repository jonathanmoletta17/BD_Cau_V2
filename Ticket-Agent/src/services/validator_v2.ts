
interface ValidationResult {
    valid: boolean;
    missingField?: string;
    message?: string;
}

export class ValidatorV2 {
    /**
     * Enforces strict business rules on the extracted payload.
     * Acts as a final gatekeeper before allowing the ticket to be completed.
     */
    static validate(intent: string, payload: any): ValidationResult {
        // 1. Generic Check
        if (!payload) {
            return { valid: false, message: "Payload is empty." };
        }

        // 2. Intent-Specific Rules
        switch (intent) {
            case 'equipment_request':
                return this.validateEquipmentRequest(payload);

            // Add other V2 intents here as they are migrated
            // case 'create_user': return this.validateCreateUser(payload);

            default:
                // For now, if no strict rules exist, we trust the Extractor (or allow it to pass)
                // In a robust system, we might want to default to false if unknown.
                return { valid: true };
        }
    }

    private static validateEquipmentRequest(payload: any): ValidationResult {
        // Rule A: request_type is mandatory
        if (!payload.request_type) {
            return { valid: false, missingField: "request_type", message: "Preciso saber se é um Incidente (quebrou) ou Requisição (novo)." };
        }

        const type = payload.request_type.toLowerCase();

        // Rule B: Incident Validation
        if (type === 'incident') {
            // Must have Description
            if (!payload.description) return { valid: false, missingField: "description", message: "Preciso de uma descrição do problema." };

            // Must have Location
            if (!payload.location) return { valid: false, missingField: "location", message: "Qual é a sua localização atual?" };

            // CRITICAL RULE: Asset Tag OR Serial Number
            // The AI often skips this if it feels "helpful". We force it here.
            if (!payload.asset_tag && !payload.serial_number) {
                return {
                    valid: false,
                    missingField: "asset_tag",
                    message: "Para incidentes com equipamentos, é OBRIGATÓRIO informar o número de Patrimônio (etiqueta) ou Serial Number. Por favor, verifique no aparelho."
                };
            }
        }

        // Rule C: Requisition Validation
        else if (type === 'requisition') {
            if (!payload.item_type) return { valid: false, missingField: "item_type", message: "Que tipo de item você precisa?" };
            if (!payload.business_reason) return { valid: false, missingField: "business_reason", message: "Qual o motivo ou justificativa para esta solicitação?" };
            if (!payload.location) return { valid: false, missingField: "location", message: "Onde devo entregar (Localização)?" };
        }

        return { valid: true };
    }
}
