
import { AgentContext } from './types';
import { SessionRepository } from '../repositories/redis_repository';
import { ExtractorService } from '../skills/extractor';
import { llmService } from '../services/llm_service';
import { isComplete, getMissingFields, FIELD_LABELS } from './validator';

export interface EngineConfig {
    persistence: SessionRepository;
    extractor: ExtractorService;
}

export interface EngineResponse {
    response: string;
    data: any;    // The extraction state (Ticket Entities)
    ticketId?: number; // If created
}

export class AgentEngine {
    private persistence: SessionRepository;
    private extractor: ExtractorService;

    constructor(config: EngineConfig) {
        this.persistence = config.persistence;
        this.extractor = config.extractor;
        console.log("[AgentEngine] Initialized with Extractor + Redis");
    }

    /**
     * Main Conversation Loop
     */
    async process(sessionId: string, message: string, userId: string = 'unknown', conversationId?: string): Promise<EngineResponse> {
        // Generate conversationId if not provided (for backwards compatibility)
        const convId = conversationId || `conv-${Date.now()}`;
        const contextKey = `${sessionId}:${convId}`;

        console.log(`[Engine] Processing msg for session:${sessionId} conversation:${convId}`);

        // 1. Load Context
        let context = await this.persistence.getSession(contextKey);
        if (!context) {
            console.log(`[Engine] New Conversation for ${contextKey}`);
            context = this.initializeContext(sessionId, userId, convId);
        }

        // 2. Append User Message
        context.history.push(`User: ${message}`);

        // 3. Semantic Extraction (The "Ear")
        // We extract entities based on the FULL history (including new message)
        const extractedState = await this.extractor.extract(context);
        context.data = extractedState; // Update State
        console.log("[Engine] State Updated:", extractedState);

        // 4. Generate Response (The "Mouth")
        // We construct a dynamic system prompt based on what we know and what is missing.
        const response = await this.generateResponse(context, message);

        // 5. Append Agent Response
        context.history.push(`Agent: ${response}`);

        // 6. Save State
        await this.persistence.saveSession(context);

        return {
            response: response,
            data: extractedState
        };
    }

    /**
     * Generates a dynamic system prompt based on current state completeness.
     * Uses validator module to determine what's missing and adapt instructions.
     */
    private generateSystemPrompt(context: AgentContext): string {
        const { data } = context;
        const intent = data.intent || null;  // Convert undefined to null
        const complete = isComplete(intent, data);
        const missingFields = getMissingFields(intent, data);

        // SCENARIO 1: All required information collected → Ask for confirmation
        if (complete) {
            const summary = `
- Intent: ${intent || 'General Request'}
- Location: ${data.location}
- Extension: ${data.extension}
- Category: ${data.category || 'N/A'}
- Description: ${data.description}`.trim();

            return `
You are an IT Support Agent. The user has provided ALL required information for their ticket.

Summary of Information:
${summary}

CRITICAL INSTRUCTION:
The information is COMPLETE. You MUST:
1. Acknowledge receipt of all information
2. Present a brief summary
3. Ask the user to CONFIRM ticket creation
4. DO NOT ask for any additional information
5. DO NOT ask about urgency, severity, timing, or impact
6. Be concise and friendly

Example response format:
"Perfeito! Tenho todas as informações necessárias:
- Local: ${data.location}
- Ramal: ${data.extension}
- Problema: ${data.description}

Posso criar o chamado agora?"
            `.trim();
        }

        // SCENARIO 2: Missing information → Ask for next specific field
        const nextField = missingFields[0];
        const fieldLabel = FIELD_LABELS[nextField] || nextField;

        // Build current info summary (only filled fields)
        const knownInfo: string[] = [];
        if (data.location) knownInfo.push(`- Local: ${data.location}`);
        if (data.extension) knownInfo.push(`- Ramal: ${data.extension}`);
        if (data.category) knownInfo.push(`- Tipo: ${data.category}`);
        if (data.description) knownInfo.push(`- Descrição: ${data.description}`);

        const knownSummary = knownInfo.length > 0
            ? `\nInformações já coletadas:\n${knownInfo.join('\n')}`
            : '';

        return `
You are an IT Support Agent collecting information for a ticket.
${knownSummary}

MISSING REQUIRED FIELD: ${nextField}
User-friendly label: "${fieldLabel}"

CRITICAL INSTRUCTIONS:
1. Ask ONLY for "${nextField}" (${fieldLabel})
2. DO NOT ask for multiple things at once
3. DO NOT ask for optional information
4. DO NOT ask about urgency, timing, severity, or impact
5. DO NOT make assumptions or creative questions
6. Be concise, friendly, and direct

Example response:
"Entendi! Só preciso de mais uma informação: ${fieldLabel}."
        `.trim();
    }

    private async generateResponse(context: AgentContext, lastUserMessage: string): Promise<string> {
        // Generate dynamic prompt based on current state
        const systemPrompt = this.generateSystemPrompt(context);

        // LLM generates friendly response following the instructions
        return await llmService.complete(lastUserMessage, systemPrompt);
    }

    private initializeContext(sessionId: string, userId: string, conversationId: string): AgentContext {
        return {
            sessionId: sessionId,
            conversationId: conversationId,
            userId: userId,
            history: [],
            data: {}
        };
    }
}
