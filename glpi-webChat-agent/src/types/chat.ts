
// V3 Types

export interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
    type?: 'TEXT' | 'FORM' | 'WIDGET';
    metadata?: any;
}

export interface ChatResponse {
    response: string;
    conversationId: string;
    ticketId?: string;
    // V3 Fields
    type?: 'TEXT' | 'FORM' | 'WIDGET';
    metadata?: any;
}

export type FieldType = 'text' | 'number' | 'date' | 'select' | 'textarea' | 'hidden';

export interface FormField {
    id: string;
    label: string;
    type: FieldType;
    required: boolean;
    options?: string[];
    value?: string | number;
    placeholder?: string;
    validationRegex?: string;
}

export interface FormSchema {
    formKey: string;
    title: string;
    description: string;
    fields: FormField[];
    submitLabel?: string;
}
