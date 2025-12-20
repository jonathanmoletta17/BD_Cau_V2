import { llmService } from "../services/llm_service";
import * as fs from 'fs';
import * as path from 'path';

async function runTest(scenarioName: string, inputs: string[], expectedFields: string[], forbiddenFields: string[] = []) {
    console.log(`\n---------------------------------------------------------`);
    console.log(`🧪 TESTING SCENARIO: ${scenarioName}`);
    console.log(`---------------------------------------------------------`);

    const docPath = path.join(process.cwd(), 'archive-docs', '20_AI_PRINTER_ISSUE.md');
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
   - Look for Locations (Rooms, floors, sectors).
   - Look for Printer Models (HP, Kyocera, Brother, etc.).
   - Look for Supplies (Toner, ink, cartridge).
   - Look for Error Descriptions.
3. Think step-by-step:
   - Identify the Issue Type (Toner vs Defect).
   - Check the doc for REQUIRED fields for that specific type.
   - List what is present and what is missing.
4. Action:
   - If fields are missing: Ask the user for them in Portuguese.
   - If all fields are present: Output a JSON object.

CRITICAL RULES:
- If user says "tinta" or "toner", type is "Toner".
- If user says "quebrada", "erro", "parou", type is "Defect".
- **Location is CRITICAL** for all requests.
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
    // 1. Happy Path Toner
    await runTest(
        "Toner Request (Complete)",
        ["Preciso de toner preto para a HP Laserjet da sala do financeiro"],
        ["issue_type", "location", "printer_model", "color"],
        []
    );

    // 2. Happy Path Defect
    await runTest(
        "Printer Defect (Complete)",
        ["A impressora do corredor do 2º andar tá fazendo um barulho estranho e mastigando papel"],
        ["issue_type", "location", "description"],
        ["color"] // Should not be present for defects usually, unless relevant
    );

    // 3. Missing Location
    await runTest(
        "Missing Location",
        ["Minha impressora parou de funcionar do nada"],
        [], // Expecting Question
        []
    );

    // 4. Missing Details for Toner
    await runTest(
        "Toner Missing Details",
        ["Acabou a tinta da impressora"],
        [], // Expecting Question about model/color
        []
    );
}

runSuite().catch(console.error);
