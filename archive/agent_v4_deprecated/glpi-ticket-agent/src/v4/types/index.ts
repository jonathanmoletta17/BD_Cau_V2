export type V3Intent = 'SERVICE_REQUEST' | 'INCIDENT' | 'CHITCHAT' | 'UNKNOWN';

export type FieldType = 'text' | 'select' | 'textarea' | 'number' | 'date';

export interface FormField {
    id: string;
    label: string;
    type: FieldType;
    required?: boolean;
    placeholder?: string;
    value?: any;
    options?: string[];
    validation?: {
        pattern?: string;
        min?: number;
        max?: number;
    };
}

export interface FormSchema {
    formKey: string;
    title: string;
    description: string;
    fields: FormField[];
    submitLabel: string;
}

export interface AgentResponse {
    type: 'TEXT' | 'FORM' | 'WIDGET';
    message: string;
    metadata?: {
        intent?: V3Intent;
        form?: FormSchema;
        widgetData?: any;
        suggestions?: string[];
        ticketId?: string;
        telemetry?: {
            agent: string;
            confidence?: number;
            reasoning?: {
                router_decision?: string;
                router_confidence?: number;
                keywords_found?: string[];
                entity_detected?: {
                    keyword: string;
                    mapped_to: { id: number; name: string };
                };
                rag_context?: {
                    entities_found: number;
                    categories_found: number;
                    rules_applied: string[];
                    relevance_score: number;
                };
                diagnostic_step?: number;
                extracted_fields?: Record<string, any>;
            };
            timing?: {
                router_ms?: number;
                agent_ms?: number;
                total_ms?: number;
            };
        };
    };
}

export interface ConversationState {
    conversationId: string;
    userId: string;
    history: { role: string; content: string }[];
    lastIntent?: V3Intent;
    slots?: Record<string, any>;
}
