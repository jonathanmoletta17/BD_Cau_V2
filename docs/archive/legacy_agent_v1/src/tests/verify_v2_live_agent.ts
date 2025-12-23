
import { TriageGraphConfigDriven } from "../agent/graph";
import { configManager } from "../agent/config_loader";
import * as dotenv from 'dotenv';
dotenv.config();

async function runScenario(name: string, input: string) {
    console.log(`\n=================================================`);
    console.log(`🚀 SCENARIO: ${name}`);
    console.log(`=================================================`);

    const graph = new TriageGraphConfigDriven();
    let state = await graph.process(input);

    console.log(`\n👤 User: "${input}"`);

    // Loop for multi-turn (limit 5)
    for (let i = 0; i < 5; i++) {
        if (state.is_complete) break;

        // If agent asks a question, we simulate an answer or stop
        const lastMsg = state.messages[state.messages.length - 1];
        if (lastMsg.role === 'agent') {
            console.log(`\n🤖 Agent Asks: ${lastMsg.content.substring(0, 100)}...`);

            // Force reply to unblock scenario
            const reply = "Meu ramal é 1234.";
            console.log(`\n👤 User (Simulated): "${reply}"`);
            state = await graph.process(reply, state);
        }
    }

    if (state.is_complete) {
        console.log(`✅ TICKET COMPLETE!`);
        console.log(`   Intent: ${state.intent}`);
        console.log(`   FINAL PAYLOAD:`, JSON.stringify(state.ticket_payload, null, 2));
    }
}

async function verify() {
    // 1. Reset Password - Should ask for RAMAL now
    await runScenario("Reset Password", "My username is j.silva. Reset my password on system Windows. URGENTE");
}

verify().catch(console.error);
