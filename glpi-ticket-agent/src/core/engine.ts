
import { AgentContext } from './types';
import { SessionRepository } from '../repositories/redis_repository';
import { ExtractorService } from '../skills/extractor';
import { llmService } from '../services/llm_service';

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
    async process(sessionId: string, message: string, userId: string = 'unknown'): Promise<EngineResponse> {
        console.log(`[Engine] Processing msg for ${sessionId}`);

        // 1. Load Context
        let context = await this.persistence.getSession(sessionId);
        if (!context) {
            console.log(`[Engine] New Session for ${sessionId}`);
            context = this.initializeContext(sessionId, userId);
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

    private async generateResponse(context: AgentContext, lastUserMessage: string): Promise<string> {
        const state = context.data;

        const systemPrompt = `
You are a helpful IT Support Agent creating a GLPI ticket.
Your goal is to collect: Title, Description, Category, Urgency, Location.

Current Known Info:
- Location: ${state.location || "UNKNOWN"}
- Extension: ${state.extension || "UNKNOWN"}
- Problem Type: ${state.problemType || "UNKNOWN"}
- Description: ${state.description || "UNKNOWN"}

Instructions:
1. Validated what you know.
2. Ask for what is missing.
3. Be concise and friendly.
4. If everything is known, ask to confirm creation.
`;

        // We use a simple completion here. 
        // In V3 we might use a "Router" to decide if we should run a tool (Create Ticket).
        return await llmService.complete(lastUserMessage, systemPrompt);
    }

    private initializeContext(sessionId: string, userId: string): AgentContext {
        return {
            sessionId: sessionId,
            userId: userId,
            history: [],
            data: {}
        };
    }
}
