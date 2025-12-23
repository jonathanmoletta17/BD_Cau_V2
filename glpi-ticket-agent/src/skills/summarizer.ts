
import { AgentContext } from '../core/types';
import { llmService } from '../services/llm_service';

export interface TicketContent {
    title: string;
    content: string;
}

export class SummaryService {

    /**
     * Generates a professional ticket title and description based on the chat history.
     * @param context The agent context containing the history.
     * @param categoryHint Optional hint about the category (e.g., "Printer", "Network").
     */
    async generateTicketContent(context: AgentContext, categoryHint: string = "General"): Promise<TicketContent | null> {
        console.log(`[SummaryService] Generating content for category: ${categoryHint}`);

        // 1. Format History
        // We filter out system messages if any, or just dump the array.
        // Assuming history is array of strings "Speaker: Message"
        const transcript = context.history.join("\n");

        if (!transcript) {
            console.warn("[SummaryService] Empty history, skipping generation.");
            return null;
        }

        // 2. prompt Construction
        const systemPrompt = `
You are an expert IT Service Desk Agent. Your job is to summarize a support chat into a professional Ticket.

RULES:
1. **Title:** Must be UPPERCASE, short, and concise. Format: "[CATEGORY] ISSUE SUMMARY".
2. **Content:** Write a professional description of the issue reported by the user. Include:
   - The user's intent/problem.
   - Any symptoms mentioned.
   - Location or specific equipment details if provided in the chat.
   - Contact info if provided.
3. Do NOT invent information not present in the chat.
4. Output must be valid JSON matching the schema below.
`;

        const userPrompt = `
Category: ${categoryHint}

Chat Transcript:
${transcript}

Expected Output JSON:
{
  "title": "uppercase title",
  "content": "professional description"
}
`;

        // 3. Call LLM
        try {
            const result = await llmService.completeJson<TicketContent>(userPrompt, systemPrompt);

            if (result && result.title && result.content) {
                console.log(`[SummaryService] Generated: ${result.title}`);
                return result;
            } else {
                console.warn("[SummaryService] LLM returned invalid structure:", result);
                return null;
            }

        } catch (e) {
            console.error("[SummaryService] Failed to generate content:", e);
            return null;
        }
    }
}
