
// src/agent/flows/types.ts

export interface AgentContext {
    userId: string;
    sessionId: string;
    data: FlowData; // Dynamic bag of collected data
    waitingFor?: string; // Explicit state tracking (e.g. 'LOCATION', 'EXTENSION')
    glpiToken?: string;
    glpiUserId?: number;
    username?: string;
    history: string[]; // Chat history
}

export interface FlowData {
    // Common fields
    intent?: string | null;
    location?: string | null;
    extension?: string | null;
    description?: string | null; // Added field

    // Printer specific
    problemType?: 'ERROR_MSG' | 'TONER' | 'PAPER_JAM' | 'INSTALLATION' | 'OTHER' | 'UNKNOWN' | 'PRINTER' | 'NETWORK' | 'COMPUTER' | null;
    problemDescription?: string | null;
    printerModel?: string | null;

    // Auth specific
    auth_step?: string | null;
    temp_username?: string | null;

    // Allow random extras
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
