import { llmService } from "./llm_service";
import { DocLoader } from "./doc_loader";

export class ExtractorV2 {

    /**
     * The new "Brain" of the agent. 
     * Uses a generic Chain-of-Thought prompt populated with the specific Intent's Governance Doc.
     * 
     * @param intent The identified intent (e.g., 'create_user')
     * @param userHistory The chat history string
     * @returns The JSON payload OR a follow-up question.
     */
    async extract(intent: string, userHistory: string): Promise<any> {
        console.log(`🧠 ExtractorV2: Processing intent '${intent}'...`);

        // 1. Load the "Brain" for this intent
        const governanceDoc = DocLoader.loadDoc(intent);
        if (!governanceDoc) {
            throw new Error(`No V2 Logic found for ${intent}`);
        }

        // 2. Construct the System Prompt (The same one validated in tests)
        const systemPrompt = `
You are an intelligent IT Agent.
You have access to the following Governance Document:

--- DOC START ---
${governanceDoc}
--- DOC END ---

INSTRUCTIONS:
1. Read the provided Dialogue History.
2. **ENTITY EXTRACTION STEP:**
   - Identify all entities required by the document.
   - respecting all "Logic Gates" (e.g., IF User Type is X, THEN Require Y).
3. Think step-by-step:
   - What fields are present?
   - What fields are missing?
   - Are there any negative constraints (fields I strictly must NOT ask for)?
4. Action:
   - If fields are missing: Ask the user a clarifying question (in Portuguese).
   - If all REQUIRED fields are present: Output a PURE JSON object containing:
     1. All "Required" fields extracted.
     2. All "Inferred" fields (inference based on context).

5. CRITICAL RULES:
- Follow the VALIDATION RULES in the doc strictly.
- **NEVER** ask for information marked as "NEGATIVE CONSTRAINT".
- Output PURE JSON (no markdown block) if complete.
`;

        // 3. Call LLM
        const response = await llmService.complete(userHistory, systemPrompt);

        // 4. Parse Response (JSON vs Text)
        const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/) || response.match(/\{[\s\S]*\}/);

        if (jsonMatch) {
            // Success: Data extraction complete
            try {
                const rawJson = jsonMatch[1] || jsonMatch[0];
                const payload = JSON.parse(rawJson);
                console.log("🧩 Extracted JSON Payload:", payload);
                return {
                    status: "COMPLETE",
                    payload: payload,
                    message: null
                };
            } catch (e) {
                console.error("❌ Failed to parse JSON from LLM response:", e);
                return {
                    status: "ERROR",
                    message: "Internal Error: Could not parse agent decision."
                };
            }
        } else {
            // Failure: Missing Data -> Agent is asking a question
            console.log("🗣️ Agent asking question:", response);
            return {
                status: "INCOMPLETE",
                message: response, // The question to show the user
                missing_info: true
            };
        }
    }
}
