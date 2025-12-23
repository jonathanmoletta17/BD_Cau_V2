
import { z } from 'zod';
import { LLMService, llmService } from '../services/llm_service';
import { AgentContext } from '../core/types';

// 1. Define the Schema (The "Contract" of what we want to know)
const TicketEntitiesSchema = z.object({
    location: z.string().nullable().optional().describe("The physical location of the user or asset (e.g., 'Sala 204', 'Prédio Anexo', 'Andar Térreo'). Null if unknown."),
    extension: z.string().nullable().optional().describe("The phone extension or 'Ramal' (e.g., '3221', '4050'). Null if unknown."),
    problemType: z.enum(['PRINTER', 'NETWORK', 'COMPUTER', 'UNKNOWN']).nullable().optional().describe("Category of the issue detected."),
    description: z.string().nullable().optional().describe("A concise summary of the reported problem.")
});

export type TicketEntities = z.infer<typeof TicketEntitiesSchema>;

export class ExtractorService {
    private llm: LLMService;

    constructor(llm: LLMService = llmService) {
        this.llm = llm;
    }

    /**
     * Analyzes the conversation history to extract the current state of entities.
     */
    async extract(context: AgentContext): Promise<TicketEntities> {
        const historyText = context.history.map(msg => msg).join("\n");

        // System Prompt: The "Listener" Persona
        const systemPrompt = `
You are an intelligent listener for an IT Support Agent. 
Your goal is to extract specific entities from the conversation history into a JSON object.

RULES:
1. **Location:** Look for room numbers, building names, floor numbers, or descriptive locations (e.g., "lá embaixo", "na recepção").
2. **Context Awareness:** If the user says "Já disse" or refers to a previous message, look back in history to find the value.
3. **Implicit Info:** If the user implies the location (e.g., "Sou do financeiro"), use "Financeiro" as location.
4. **Correction:** If the user corrects a value (e.g., "Não, sala 305"), use the NEW value.
5. Return JSON only matching this schema:
   {
     "location": string | null,
     "extension": string | null,
     "problemType": "PRINTER" | "NETWORK" | "COMPUTER" | "UNKNOWN" | null,
     "description": string | null
   }
`;

        const userPrompt = `
Current Conversation History:
---
${historyText}
---

Extract the current state of entities.
`;

        try {
            console.log("[Extractor] Analysing history...");
            const json = await this.llm.completeJson<any>(userPrompt, systemPrompt);

            if (!json) return this.getEmpty();

            // Validate with Zod
            const result = TicketEntitiesSchema.safeParse(json);

            if (result.success) {
                console.log("[Extractor] Success:", result.data);
                return result.data;
            } else {
                console.warn("[Extractor] Schema mismatch:", result.error);
                // Return partials or empty? Let's try to salvage valid fields manually if Zod is too strict, 
                // but for now return safe defaults mixed with valid props.
                return { ...this.getEmpty(), ...json };
            }

        } catch (e) {
            console.error("[Extractor] Failed:", e);
            return this.getEmpty();
        }
    }

    private getEmpty(): TicketEntities {
        return {
            location: null,
            extension: null,
            problemType: null,
            description: null
        };
    }
}
