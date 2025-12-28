import { describe, it, expect } from '@jest/globals';
import {
    ChatInputSchema,
    CreateUserSchema,
    CreateTicketSchema,
    validatePayload,
    formatValidationErrors
} from '../validation';

describe('ChatInputSchema', () => {
    it('should validate correct chat input', () => {
        const payload = {
            message: 'Minha impressora não funciona',
            sessionId: 'session-123',
            conversationId: 'conv-456'
        };

        const result = validatePayload(ChatInputSchema, payload);
        expect(result.success).toBe(true);
        expect(result.data).toEqual(payload);
    });

    it('should reject empty message', () => {
        const payload = {
            message: '',
            sessionId: 'session-123'
        };

        const result = validatePayload(ChatInputSchema, payload);
        expect(result.success).toBe(false);
        expect(result.errors).toBeDefined();
    });

    it('should reject too long message', () => {
        const payload = {
            message: 'a'.repeat(1001),
            sessionId: 'session-123'
        };

        const result = validatePayload(ChatInputSchema, payload);
        expect(result.success).toBe(false);
    });

    it('should reject invalid sessionId', () => {
        const payload = {
            message: 'Hello',
            sessionId: '123' // too short
        };

        const result = validatePayload(ChatInputSchema, payload);
        expect(result.success).toBe(false);
    });
});

describe('CreateUserSchema', () => {
    it('should validate correct user payload', () => {
        const payload = {
            name: 'João Silva',
            entity: 'SECOM',
            entityId: 7,
            email: 'joao@example.com',
            phone: '+55 11 98765-4321'
        };

        const result = validatePayload(CreateUserSchema, payload);
        expect(result.success).toBe(true);
    });

    it('should reject invalid email', () => {
        const payload = {
            name: 'João Silva',
            entity: 'SECOM',
            entityId: 7,
            email: 'not-an-email'
        };

        const result = validatePayload(CreateUserSchema, payload);
        expect(result.success).toBe(false);
    });

    it('should reject negative entityId', () => {
        const payload = {
            name: 'João Silva',
            entity: 'SECOM',
            entityId: -1
        };

        const result = validatePayload(CreateUserSchema, payload);
        expect(result.success).toBe(false);
    });

    it('should allow optional fields', () => {
        const payload = {
            name: 'João Silva',
            entity: 'SECOM',
            entityId: 7
            // email e phone opcionais
        };

        const result = validatePayload(CreateUserSchema, payload);
        expect(result.success).toBe(true);
    });
});

describe('CreateTicketSchema', () => {
    it('should validate correct ticket payload', () => {
        const payload = {
            title: 'Problema com impressora',
            description: 'A impressora HP LaserJet não está imprimindo documentos',
            category: 'Hardware',
            priority: 'high' as const
        };

        const result = validatePayload(CreateTicketSchema, payload);
        expect(result.success).toBe(true);
    });

    it('should use default priority', () => {
        const payload = {
            title: 'Problema com impressora',
            description: 'A impressora HP LaserJet não está imprimindo documentos'
        };

        const result = validatePayload(CreateTicketSchema, payload);
        expect(result.success).toBe(true);
        expect(result.data?.priority).toBe('medium');
    });

    it('should reject invalid priority', () => {
        const payload = {
            title: 'Problema com impressora',
            description: 'A impressora HP LaserJet não está imprimindo documentos',
            priority: 'critical' // não existe
        };

        const result = validatePayload(CreateTicketSchema, payload);
        expect(result.success).toBe(false);
    });

    it('should reject too short title', () => {
        const payload = {
            title: 'Bug',
            description: 'A impressora HP LaserJet não está imprimindo documentos'
        };

        const result = validatePayload(CreateTicketSchema, payload);
        expect(result.success).toBe(false);
    });
});

describe('formatValidationErrors', () => {
    it('should format errors correctly', () => {
        const payload = {
            message: '',
            sessionId: '12'
        };

        const result = validatePayload(ChatInputSchema, payload);
        expect(result.success).toBe(false);

        const formatted = formatValidationErrors(result.errors!);
        expect(formatted['message']).toContain('Message cannot be empty');
        expect(formatted['sessionId']).toContain('Invalid session ID');
    });
});
