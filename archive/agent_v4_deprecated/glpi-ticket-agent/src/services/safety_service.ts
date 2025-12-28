/**
 * Safety Service - Sprint 3.4
 * Detecção de prompt injection e conteúdo suspeito
 */

export interface SafetyCheckResult {
    isSafe: boolean;
    reason?: string;
    confidence: number;
    detectedPatterns?: string[];
}

export class SafetyService {
    private readonly suspiciousPatterns = [
        // Comandos de sistema
        { pattern: /ignore\s+(previous|above|all)\s+instructions?/i, name: 'ignore_instructions' },
        { pattern: /system\s*:\s*/i, name: 'system_prefix' },
        { pattern: /you\s+are\s+(now|a)\s+/i, name: 'role_manipulation' },

        // Tentativas de roleplay
        { pattern: /\[system\]/i, name: 'system_tag' },
        { pattern: /<system>/i, name: 'system_xml' },
        { pattern: /<\|im_start\|>/i, name: 'chat_markup' },
        { pattern: /##\s*system/i, name: 'markdown_system' },

        // Bypass
        { pattern: /forget\s+everything/i, name: 'forget_command' },
        { pattern: /disregard\s+(your|the)\s+/i, name: 'disregard_command' },
        { pattern: /new\s+instructions?:/i, name: 'new_instructions' },

        // Vazamento de prompt
        { pattern: /what\s+(is|are)\s+your\s+(instructions?|prompt)/i, name: 'prompt_leak_attempt' },
        { pattern: /show\s+me\s+your\s+prompt/i, name: 'show_prompt' },
        { pattern: /reveal\s+your\s+system/i, name: 'reveal_system' },

        // Jailbreak
        { pattern: /DAN|do\s+anything\s+now/i, name: 'dan_jailbreak' },
        { pattern: /grandma|grandmother\s+trick/i, name: 'grandma_exploit' },
    ];

    /**
     * Detectar tentativas de prompt injection
     */
    detectPromptInjection(input: string): SafetyCheckResult {
        const detected: string[] = [];

        // Verificar padrões suspeitos
        for (const { pattern, name } of this.suspiciousPatterns) {
            if (pattern.test(input)) {
                detected.push(name);
            }
        }

        if (detected.length > 0) {
            return {
                isSafe: false,
                reason: `Suspicious patterns detected: ${detected.join(', ')}`,
                confidence: 0.8,
                detectedPatterns: detected
            };
        }

        // Detectar excesso de caracteres especiais
        const specialCharsCheck = this.checkSpecialCharacters(input);
        if (!specialCharsCheck.isSafe) {
            return specialCharsCheck;
        }

        // Detectar encoding suspeito
        const encodingCheck = this.checkSuspiciousEncoding(input);
        if (!encodingCheck.isSafe) {
            return encodingCheck;
        }

        return {
            isSafe: true,
            confidence: 1.0
        };
    }

    /**
     * Verificar excesso de caracteres especiais
     */
    private checkSpecialCharacters(input: string): SafetyCheckResult {
        const specialChars = (input.match(/[<>{}[\]|\\]/g) || []).length;
        const ratio = specialChars / input.length;

        if (ratio > 0.1) { // > 10% caracteres especiais
            return {
                isSafe: false,
                reason: 'Excessive special characters',
                confidence: 0.6
            };
        }

        return { isSafe: true, confidence: 1.0 };
    }

    /**
     * Verificar encoding suspeito (base64, hex, etc)
     */
    private checkSuspiciousEncoding(input: string): SafetyCheckResult {
        // Detectar possível Base64
        const base64Pattern = /[A-Za-z0-9+/]{50,}={0,2}/;
        if (base64Pattern.test(input) && input.length > 100) {
            return {
                isSafe: false,
                reason: 'Possible Base64 encoded payload',
                confidence: 0.5
            };
        }

        // Detectar excesso de escape sequences
        const escapePattern = /\\x[0-9a-fA-F]{2}/g;
        const escapes = (input.match(escapePattern) || []).length;
        if (escapes > 5) {
            return {
                isSafe: false,
                reason: 'Excessive escape sequences',
                confidence: 0.6
            };
        }

        return { isSafe: true, confidence: 1.0 };
    }

    /**
     * Detectar conteúdo impróprio (placeholder)
     */
    detectInappropriateContent(input: string): SafetyCheckResult {
        // TODO: Implementar detecção de conteúdo ofensivo
        // Pode integrar com serviços como Perspective API ou Azure Content Moderator

        return {
            isSafe: true,
            confidence: 1.0
        };
    }

    /**
     * Sanitizar input removendo caracteres perigosos
     */
    sanitizeInput(input: string): string {
        return input
            .replace(/<script[^>]*>.*?<\/script>/gi, '') // Remove scripts
            .replace(/javascript:/gi, '')                 // Remove javascript: URIs
            .replace(/on\w+\s*=/gi, '')                   // Remove event handlers
            .trim();
    }

    /**
     * Validar comprimento do input
     */
    validateLength(input: string, maxLength: number = 1000): SafetyCheckResult {
        if (input.length > maxLength) {
            return {
                isSafe: false,
                reason: `Input too long (${input.length} > ${maxLength})`,
                confidence: 1.0
            };
        }

        return {
            isSafe: true,
            confidence: 1.0
        };
    }

    /**
     * Validação completa (combo de todas as checagens)
     */
    validateInput(input: string): SafetyCheckResult {
        // 1. Validar comprimento
        const lengthCheck = this.validateLength(input);
        if (!lengthCheck.isSafe) {
            return lengthCheck;
        }

        // 2. Detectar prompt injection
        const injectionCheck = this.detectPromptInjection(input);
        if (!injectionCheck.isSafe) {
            return injectionCheck;
        }

        // 3. Detectar conteúdo impróprio
        const contentCheck = this.detectInappropriateContent(input);
        if (!contentCheck.isSafe) {
            return contentCheck;
        }

        return {
            isSafe: true,
            confidence: 1.0
        };
    }
}
