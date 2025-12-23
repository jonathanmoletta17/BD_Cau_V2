import { llmService } from "../services/llm_service";
import * as fs from 'fs';
import * as path from 'path';

async function runTest(scenarioName: string, inputs: string[], expectedFields: string[], forbiddenFields: string[] = []) {
    console.log(`\n---------------------------------------------------------`);
    console.log(`🧪 TESTING SCENARIO: ${scenarioName}`);
    console.log(`---------------------------------------------------------`);

    const docPath = path.join(process.cwd(), 'archive-docs', '17_AI_OPTIMIZED.md');
    const governanceDoc = fs.readFileSync(docPath, 'utf-8');

    const systemPrompt = `
You are an intelligent IT Agent.
You have access to the following Governance Document:

--- DOC START ---
${governanceDoc}
--- DOC END ---

INSTRUCTIONS:
1. Read the User Input.
2. **ENTITY EXTRACTION STEP:**
   - Look for proper names -> Candidate for 'full_name'.
   - Look for department names (RH, TI, Design, etc.) -> Candidate for 'department'.
   - Look for ID patterns (CPF, RG, numbers).
3. Think step-by-step:
   - Identify the intent (is it CREATE_USER?).
   - Identify the user type (Efetivo or Estagiário).
   - Check the doc for REQUIRED fields for that specific type.
   - List what is present and what is missing.
4. Action:
   - If fields are missing: Ask the user for them in Portuguese.
   - If all fields are present: Output a JSON object.

CRITICAL RULES:
- If user says "estagiário", the type is "Estagiário".
- For "Estagiário", the Doc says "Exige RG". Do NOT ask for CPF/Matricula.
- For "Efetivo", the Doc says "Exige CPF E Matrícula".
- **Assume names like "Carlos", "Kevin", "João" are the full_name if no other name is present.**
- Output PURE JSON if complete.
`;

    let history = "";
    let finalPayload: any = null;

    for (const userInput of inputs) {
        console.log(`👤 User: "${userInput}"`);
        history += `\nUser: ${userInput}`;
        const prompt = `Current Dialogue History:\n${history}\n\nAgent Response:`;
        const response = await llmService.complete(prompt, systemPrompt);
        console.log(`🤖 Agent: ${response}`);
        history += `\nAgent: ${response}`;

        // Helper to extract JSON from markdown/text
        const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/) || response.match(/\{[\s\S]*\}/);

        if (jsonMatch) {
            const rawJson = jsonMatch[1] || jsonMatch[0];
            try {
                finalPayload = JSON.parse(rawJson);
                console.log("🧩 Extracted JSON from CoT response.");
            } catch (e) {
                console.error("⚠️ Failed to parse extracted JSON block.");
            }
        }
    }

    // Validation
    if (finalPayload) {
        console.log(`🔍 Final Payload:`, finalPayload);
        const keys = Object.keys(finalPayload);

        const missing = expectedFields.filter(k => !keys.includes(k));
        const forbiddenPresent = forbiddenFields.filter(k => keys.includes(k));

        if (missing.length === 0 && forbiddenPresent.length === 0) {
            console.log(`✅ TEST PASSED`);
        } else {
            console.error(`❌ TEST FAILED`);
            if (missing.length > 0) console.error(`   Missing fields: ${missing.join(', ')}`);
            if (forbiddenPresent.length > 0) console.error(`   Forbidden fields present: ${forbiddenPresent.join(', ')}`);
        }
    } else {
        console.log(`⚠️ No JSON payload output (Agent might be asking questions). Check logs.`);
    }
}

async function runSuite() {
    // 1. Happy Path Estagiário
    await runTest(
        "Start Intern (All Data)",
        ["Quero criar conta para o estagiário Kevin no Design. RG dele é 11222333-4"],
        ["full_name", "department", "rg", "user_type"],
        ["matricula", "cpf"]
    );

    // 2. Missing Data Estagiário
    await runTest(
        "Intern Missing RG",
        ["Novo estagiário João no TI"],
        [], // Expecting no JSON, just a question
        []
    );

    // 3. Efetivo missing Matricula
    await runTest(
        "Efetivo Missing Matricula",
        ["Novo funcionário Carlos no RH, CPF 123.456.789-00"],
        [], // Expecting Question
        []
    );
}

runSuite().catch(console.error);
