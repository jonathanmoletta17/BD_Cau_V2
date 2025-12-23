import { llmService } from "../services/llm_service";
import * as fs from 'fs';
import * as path from 'path';

async function runAgentV2() {
    console.log("--- 🤖 Agent V2 (Doc-Driven) PoC ---");

    // 1. Load the Governance Document (The "Brain")
    const docPath = path.join(process.cwd(), 'archive-docs', '17_AI_OPTIMIZED.md');
    let governanceDoc = "";
    try {
        governanceDoc = fs.readFileSync(docPath, 'utf-8');
        console.log("✅ Loaded Governance Doc: 17_AI_OPTIMIZED.md");
    } catch (e) {
        console.error("Failed to load docs", e);
        return;
    }

    // 2. Define the System Prompt (The "Personality" & "Context")
    const systemPrompt = `
You are an intelligent IT Agent.
You have access to the following Governance Document:

--- DOC START ---
${governanceDoc}
--- DOC END ---

INSTRUCTIONS:
1. Read the User Input.
2. Think step-by-step:
   - Identify the intent (is it CREATE_USER?).
   - Identify the user type (Efetivo or Estagiário).
   - Check the doc for REQUIRED fields for that specific type.
   - List what is present and what is missing.
3. Action:
   - If fields are missing: Ask the user for them in Portuguese.
   - If all fields are present: Output a JSON object.

CRITICAL RULES:
- If user says "estagiário", the type is "Estagiário".
- For "Estagiário", the Doc says "Exige RG". Do NOT ask for CPF/Matricula.
- For "Efetivo", the Doc says "Exige CPF E Matrícula".
- Output PURE JSON if complete.

Response Format:
Just the Text Question OR the JSON.
`;

    // 3. Simulate Inputs
    const inputs = [
        "Quero criar uma conta pro novo estagiário, o Kevin.",
        "É para o setor de Design. O RG dele é 11.222.333-4."
    ];

    let history = "";

    for (const userInput of inputs) {
        console.log(`\n👤 User: "${userInput}"`);
        history += `\nUser: ${userInput}`;

        const prompt = `Current Dialogue History:\n${history}\n\nAgent Response:`;

        // Call LLM
        const response = await llmService.complete(prompt, systemPrompt);
        console.log(`🤖 Agent: ${response}`);

        history += `\nAgent: ${response}`;
    }
}

runAgentV2().catch(console.error);
