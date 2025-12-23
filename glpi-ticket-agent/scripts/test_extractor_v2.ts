
import { ExtractorService } from '../src/skills/extractor';
import { AgentContext } from '../src/core/types';

// Mock Context Helper
function createMockContext(history: string[]): AgentContext {
    return {
        sessionId: 'test-session',
        userId: 'tester',
        history: history,
        data: {}
    };
}

async function runTests() {
    const extractor = new ExtractorService();

    console.log("🧪 Starting Exhaustive Extractor Tests (V2)\n");

    const scenarios = [
        {
            name: "Scenario 1: Simple One-Shot",
            history: [
                "User: Minha impressora na sala 202 está com papel atolado."
            ],
            expected: { location: "sala 202", problemType: "PRINTER" }
        },
        {
            name: "Scenario 2: The 'Logic Gap' Fix (User complains 'I already said')",
            history: [
                "User: Estou no Palácio Piratini 4 andar, impressora com erro.",
                "Agent: Qual sua sala?",
                "User: Eu já disse isso."
            ],
            // Expectation: LLM should look back and find 'Palácio Piratini 4 andar'
            expected: { location: "Palácio Piratini 4 andar" }
        },
        {
            name: "Scenario 3: Fragmented Info",
            history: [
                "User: Oi",
                "Agent: Olá",
                "User: Ramal 3321",
                "User: O problema é rede",
                "User: Setor financeiro"
            ],
            expected: { extension: "3321", problemType: "NETWORK", location: "Setor financeiro" }
        }
    ];

    for (const test of scenarios) {
        console.log(`\n----------------------------------------`);
        console.log(`▶️  Running: ${test.name}`);
        console.log(`📝 History:\n${test.history.map(l => `   ${l}`).join('\n')}`);

        const start = Date.now();
        const result = await extractor.extract(createMockContext(test.history));
        const cleanJson = JSON.stringify(result, null, 2);
        const duration = Date.now() - start;

        console.log(`\n🤖 Extracted (${duration}ms):`);
        console.log(cleanJson);

        // Simple Assertions (String matching for demo)
        let pass = true;
        for (const [key, val] of Object.entries(test.expected)) {
            const actual = (result as any)[key];
            if (!actual || !actual.toLowerCase().includes(val.toLowerCase())) {
                console.error(`❌ FAIL: Expected ${key} to contain '${val}', got '${actual}'`);
                pass = false;
            }
        }

        if (pass) console.log("✅ RESULT: PASS");
    }
}

runTests();
