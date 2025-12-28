
// src/agent/flows/types.ts

export interface AgentContext {
    userId: string;
    sessionId: string;
    conversationId: string;   // Specific conversation identifier
    data: FlowData; // Dynamic bag of collected data
    waitingFor?: string; // Explicit state tracking (e.g. 'LOCATION', 'EXTENSION')
    glpiToken?: string;
    glpiUserId?: number;
    username?: string;
    history: string[]; // Chat history
}

export interface FlowData {
    // Intent classification (for directing conversation flow)
    intent?: string | null;

    // Core fields (common to all intents)
    location?: string | null;
    extension?: string | null;
    description?: string | null;

    // Category - Dynamic string resolved by TaxonomyService
    // No hardcoded enums! LLM extracts in natural language (e.g., "Impressora", "Toner", "Wifi")
    category?: string | null;

    // Intent-specific fields
    targetSystem?: string | null;     // For RESET_PASSWORD
    printerName?: string | null;      // For PRINTER_ISSUE (optional)

    // Extensibility for intent-specific fields
    [key: string]: any;
}

export interface FlowResponse {
    type: 'QUESTION' | 'ACTION' | 'TRANSITION' | 'RESPONSE';
    message?: string; // Message to user
    nextState?: string; // If transition
    payload?: any; // If action (e.g. create ticket payload)
}

export interface FlowState {
    name: string;
    handle(context: AgentContext, message: string): Promise<FlowResponse>;
}
