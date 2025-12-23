
import { SummaryService } from '../src/skills/summarizer';
import { AgentContext } from '../src/core/types';

// Mock Context
const mockContext: AgentContext = {
    sessionId: 'test-summary',
    userId: 'test-user',
    history: [
        "Agent: Olá. Identifique-se.",
        "User: thales-leite",
        "Agent: Senha?",
        "User: *****",
        "Agent: Login OK.",
        "User: Minha impressora no RH (sala 202) não está puxando papel e faz barulho estranho.",
        "Agent: Qual seu ramal?",
        "User: 8899"
    ],
    data: {
        location: "sala 202",
        extension: "8899"
    }
};

async function test() {
    console.log("🧪 Testing SummaryService with Llama 3.1...");
    const service = new SummaryService();

    try {
        const result = await service.generateTicketContent(mockContext, "Printer/Impressora");
        console.log("\n✅ Result Recieved:");
        console.log("--------------------------------------------------");
        console.log(JSON.stringify(result, null, 2));
        console.log("--------------------------------------------------");

        if (result && result.title === result.title.toUpperCase()) {
            console.log("✅ Validation Passed: Title is Uppercase.");
        } else {
            console.log("❌ Validation Failed: Title format incorrect.");
            process.exit(1);
        }

    } catch (e) {
        console.error("❌ Service Failed:", e);
        process.exit(1);
    }
}

test();
