import { z } from 'zod';

/**
 * Validation Schemas para Guardrails de Governança
 * Sprint 3.1 - Validação de Payloads
 */

// ========== Chat Input ==========
export const ChatInputSchema = z.object({
    message: z.string()
        .min(1, 'Message cannot be empty')
        .max(1000, 'Message too long (max 1000 chars)'),
    sessionId: z.string()
        .min(5, 'Invalid session ID'),
    conversationId: z.string()
        .optional(),
    userId: z.string()
        .optional()
});

export type ChatInput = z.infer<typeof ChatInputSchema>;

// ========== Create User ==========
export const CreateUserSchema = z.object({
    name: z.string()
        .min(3, 'Name too short')
        .max(100, 'Name too long'),
    entity: z.string()
        .min(2, 'Entity name too short'),
    entityId: z.number()
        .int('Entity ID must be integer')
        .positive('Entity ID must be positive'),
    jobTitle: z.string()
        .max(100)
        .optional(),
    email: z.string()
        .email('Invalid email format')
        .optional(),
    phone: z.string()
        .regex(/^\+?[\d\s()-]{8,20}$/, 'Invalid phone format')
        .optional()
});

export type CreateUserPayload = z.infer<typeof CreateUserSchema>;

// ========== Create Ticket ==========
export const CreateTicketSchema = z.object({
    title: z.string()
        .min(5, 'Title too short')
        .max(200, 'Title too long'),
    description: z.string()
        .min(10, 'Description too short')
        .max(2000, 'Description too long'),
    category: z.string()
        .optional(),
    priority: z.enum(['low', 'medium', 'high', 'urgent'])
        .default('medium'),
    requesterId: z.number()
        .int()
        .positive()
        .optional(),
    entityId: z.number()
        .int()
        .positive()
        .optional()
});

export type CreateTicketPayload = z.infer<typeof CreateTicketSchema>;

// ========== Form Submit (Generic) ==========
export const FormSubmitSchema = z.object({
    conversationId: z.string()
        .min(5),
    data: z.record(z.any()), // Flexible form data
    confirmed: z.boolean()
        .default(false)
});

export type FormSubmitPayload = z.infer<typeof FormSubmitSchema>;

// ========== Helper Functions ==========

export interface ValidationResult<T> {
    success: boolean;
    data?: T;
    errors?: z.ZodError;
}

/**
 * Validar payload usando schema Zod
 */
export function validatePayload<T>(
    schema: z.ZodSchema<T>,
    payload: unknown
): ValidationResult<T> {
    const result = schema.safeParse(payload);

    if (result.success) {
        return {
            success: true,
            data: result.data
        };
    } else {
        return {
            success: false,
            errors: result.error
        };
    }
}

/**
 * Formatar erros Zod para resposta HTTP
 */
export function formatValidationErrors(error: z.ZodError): Record<string, string[]> {
    const formatted: Record<string, string[]> = {};

    for (const issue of error.issues) {
        const path = issue.path.join('.');
        if (!formatted[path]) {
            formatted[path] = [];
        }
        formatted[path].push(issue.message);
    }

    return formatted;
}

/**
 * Middleware factory para validação Express
 */
export function createValidationMiddleware<T>(schema: z.ZodSchema<T>) {
    return (req: any, res: any, next: any) => {
        const validation = validatePayload(schema, req.body);

        if (!validation.success) {
            return res.status(400).json({
                error: 'Validation failed',
                details: formatValidationErrors(validation.errors!)
            });
        }

        // Substituir body com dados validados
        req.body = validation.data;
        next();
    };
}
