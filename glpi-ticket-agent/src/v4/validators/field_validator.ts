/**
 * Validação de campos extraídos pelo LLM
 * Garante que os dados fazem sentido antes de gerar formulário
 */

export interface ExtractedFields {
    name?: string;
    entity?: string;
    jobTitle?: string;
    email?: string;
    phone?: string;
    validated: boolean;
    missingFields: string[];
    warnings: string[];
}

export class FieldValidator {
    /**
     * Valida nome completo
     */
    static validateName(name: string | undefined): { valid: boolean; error?: string } {
        if (!name || name.trim().length === 0) {
            return { valid: false, error: 'Nome é obrigatório' };
        }

        const trimmed = name.trim();

        // Nome deve ter pelo menos 2 palavras (nome + sobrenome)
        const words = trimmed.split(/\s+/);
        if (words.length < 2) {
            return { valid: false, error: 'Nome deve conter nome e sobrenome' };
        }

        // Cada palavra deve ter pelo menos 2 caracteres
        if (words.some(w => w.length < 2)) {
            return { valid: false, error: 'Nome inválido (palavras muito curtas)' };
        }

        // Não pode ter números
        if (/\d/.test(trimmed)) {
            return { valid: false, error: 'Nome não pode conter números' };
        }

        // Não pode ter caracteres especiais excessivos
        if (/[^\w\sáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ.-]/.test(trimmed)) {
            return { valid: false, error: 'Nome contém caracteres inválidos' };
        }

        return { valid: true };
    }

    /**
     * Valida órgão/entidade
     */
    static validateEntity(entity: string | undefined, knownEntities: string[]): { valid: boolean; error?: string; suggestion?: string } {
        if (!entity || entity.trim().length === 0) {
            return { valid: false, error: 'Órgão é obrigatório' };
        }

        const trimmed = entity.trim();

        // Verificar se é uma entidade conhecida (case-insensitive)
        const found = knownEntities.find(e =>
            e.toLowerCase() === trimmed.toLowerCase()
        );

        if (found) {
            return { valid: true };
        }

        // Fuzzy match simples
        const similarEntity = knownEntities.find(e =>
            e.toLowerCase().includes(trimmed.toLowerCase()) ||
            trimmed.toLowerCase().includes(e.toLowerCase())
        );

        if (similarEntity) {
            return {
                valid: false,
                error: `Órgão não encontrado: "${trimmed}"`,
                suggestion: similarEntity
            };
        }

        return {
            valid: false,
            error: `Órgão desconhecido: "${trimmed}". Entidades disponíveis: ${knownEntities.slice(0, 5).join(', ')}...`
        };
    }

    /**
     * Valida cargo
     */
    static validateJobTitle(jobTitle: string | undefined): { valid: boolean; error?: string } {
        if (!jobTitle || jobTitle.trim().length === 0) {
            // Cargo é opcional em alguns casos
            return { valid: true };
        }

        const trimmed = jobTitle.trim();

        // Deve ter pelo menos 3 caracteres
        if (trimmed.length < 3) {
            return { valid: false, error: 'Cargo inválido (muito curto)' };
        }

        // Não pode ter apenas números
        if (/^\d+$/.test(trimmed)) {
            return { valid: false, error: 'Cargo não pode ser apenas números' };
        }

        return { valid: true };
    }

    /**
     * Valida email (opcional)
     */
    static validateEmail(email: string | undefined): { valid: boolean; error?: string } {
        if (!email || email.trim().length === 0) {
            // Email é opcional
            return { valid: true };
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.trim())) {
            return { valid: false, error: 'Email inválido' };
        }

        return { valid: true };
    }

    /**
     * Valida todos os campos de uma vez
     */
    static validateAll(
        fields: Partial<ExtractedFields>,
        knownEntities: string[]
    ): ExtractedFields {
        const warnings: string[] = [];
        const missingFields: string[] = [];

        // Validar nome
        const nameValidation = this.validateName(fields.name);
        if (!nameValidation.valid) {
            missingFields.push('name');
            warnings.push(nameValidation.error || 'Nome inválido');
        }

        // Validar entidade
        const entityValidation = this.validateEntity(fields.entity, knownEntities);
        if (!entityValidation.valid) {
            missingFields.push('entity');
            warnings.push(entityValidation.error || 'Entidade inválida');
            if (entityValidation.suggestion) {
                warnings.push(`Você quis dizer "${entityValidation.suggestion}"?`);
            }
        }

        // Validar cargo (opcional)
        const jobTitleValidation = this.validateJobTitle(fields.jobTitle);
        if (!jobTitleValidation.valid) {
            warnings.push(jobTitleValidation.error || 'Cargo inválido');
        }

        // Validar email (opcional)
        const emailValidation = this.validateEmail(fields.email);
        if (!emailValidation.valid) {
            warnings.push(emailValidation.error || 'Email inválido');
        }

        return {
            name: fields.name,
            entity: fields.entity,
            jobTitle: fields.jobTitle,
            email: fields.email,
            phone: fields.phone,
            validated: missingFields.length === 0 && warnings.length === 0,
            missingFields,
            warnings
        };
    }
}
