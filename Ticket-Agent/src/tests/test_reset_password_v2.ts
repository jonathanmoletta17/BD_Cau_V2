import { llmService } from "../services/llm_service";
import * as fs from 'fs';
import * as path from 'path';

async function runTest(scenarioName: string, inputs: string[], expectedFields: string[], forbiddenFields: string[] = []) {
    console.log(`\n---------------------------------------------------------`);
    console.log(`🧪 TESTING SCENARIO: ${scenarioName}`);
    console.log(`---------------------------------------------------------`);

    const docPath = path.join(process.cwd(), 'archive-docs', '21_AI_RESET_PASSWORD.md');
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
   - Detect Target System (Windows/AD, Email, SAP, etc.) using logic rules.
   - Detect Username/Login.
   - Detect if User provided a password (SECURITY RISK).
3. Think step-by-step:
   - Apply Inference Rules (Default to Windows?).
   - Check Required Fields.
   - Check Security Protocols.
4. Action:
   - If fields are missing: Ask the user.
   - If complete: Output JSON.

CRITICAL RULES:
- **DEFAULT TO WINDOWS/REDE** if vague.
- **NEVER** include passwords in output.
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
            // value check
            if (finalPayload.target_system === "Rede/Windows" && scenarioName.includes("Vague")) {
                console.log(`✅ TEST PASSED (Default system applied)`);
            } else if (finalPayload.password || finalPayload.current_password) {
                console.error(`❌ SECURITY FAIL: Password included in payload!`);
            } else {
                console.log(`✅ TEST PASSED`);
            }
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
    // 1. Vague Request -> Should default to Rede/Windows
    await runTest(
        "Vague Request (Defaulting)",
        ["Esqueci minha senha, o login é j.silva"],
        ["target_system", "username"],
        ["password"]
    );

    // 2. Specific Request (Email)
    await runTest(
        "Email Reset",
        ["Meu Outlook bloqueou, usuario 1234"],
        ["target_system", "username"],
        []
    );

    // 3. Missing Username
    await runTest(
        "Missing Username",
        ["Preciso resetar a senha do SAP"],
        [], // Expecting Question
        []
    );

    // 4. Security Leak (User sends password)
    await runTest(
        "Security Leak check",
        ["Reseta minha senha do windows (usuario: bob), pode por a senha 'Banana123'"],
        ["target_system", "username"],
        ["password", "new_password", "banana123"] // Ensure password is NOT in JSON
    );
}

runSuite().catch(console.error);
