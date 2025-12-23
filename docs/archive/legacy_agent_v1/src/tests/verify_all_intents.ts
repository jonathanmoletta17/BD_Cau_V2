
import { TriageGraphConfigDriven } from "../agent/graph";
import * as dotenv from 'dotenv';
dotenv.config();

const MOCK_SYSTEM_INFO = {
    System: { Hostname: "TEST-PC", OS: "Windows 11", Build: "22621" },
    Network: { IP: "192.168.1.100" },
    Hardware: { SerialNumber: "TEST-SERIAL-123" }
};

async function runScenario(name: string, input: string) {
    console.log(`\n=================================================`);
    console.log(`🚀 SCENARIO: ${name}`);
    console.log(`=================================================`);

    const graph = new TriageGraphConfigDriven();
    // Pass mock system info
    let state = await graph.process(input, undefined, MOCK_SYSTEM_INFO);

    console.log(`\n👤 User: "${input}"`);

    // Loop for multi-turn (limit 5)
    for (let i = 0; i < 5; i++) {
        if (state.is_complete) break;

        const lastMsg = state.messages[state.messages.length - 1];
        if (lastMsg.role === 'agent') {
            console.log(`\n🤖 Agent Asks: ${lastMsg.content.substring(0, 150)}...`);

            // Heuristic to answer questions
            let reply = "1234"; // Default Ramal
            if (lastMsg.content.toLowerCase().includes("cpf")) reply = "123.456.789-00";
            if (lastMsg.content.toLowerCase().includes("matricula")) reply = "99999";

            console.log(`\n👤 User (Simulated): "${reply}"`);

            // Pass MOCK_SYSTEM_INFO again (though state should persist, good to be safe if logic changed)
            // Actually graph.process preserves state.system_info if passed in previousState, 
            // but let's just pass previousState.
            state = await graph.process(reply, state);
        }
    }

    if (state.is_complete) {
        console.log(`✅ TICKET COMPLETE!`);
        console.log(`   Intent: ${state.intent}`);
        console.log(`   FINAL PAYLOAD:`, JSON.stringify(state.ticket_payload, null, 2));

        // Verify System Info in Content
        const sysMsg = state.messages.find(m => m.content.includes("(SYSTEM) Mapped"));
        if (sysMsg) {
            console.log(`   GLPI Result Log: ${sysMsg.content}`);

            // Extract the content from the log or state if possible, but since we can't easily get the local 'ticketData' variable from here,
            // we rely on the fact that we've unit tested the mapper. 
            // However, to be thorough, let's re-map it here using the same utility to see what it WOULD be.

            // Re-importing locally to simulate the final step
            const { PayloadMapper } = require('../services/payload_mapper'); // CommonJS require for simplicity in this script context if needed, or use import if module

            // Since we use tsx, standard import works but inside a function is async. 
            // Let's just trust the unit test for the EXACT format, but we can verify the state has the info.

            console.log(`   System Info in State:`, JSON.stringify(state.system_info, null, 2));

        } else {
            console.log(`   ⚠️ WARNING: GLPI Mapping message not found.`);
        }
    } else {
        console.log(`🛑 FAILED to complete scenario.`);
        console.log(`   Last Msg: ${state.messages[state.messages.length - 1].content}`);
    }
}

async function verify() {
    // 1. Reset Password
    await runScenario("Reset Password", "My username is j.silva. Reset my password on system Windows. URGENTE");

    // 2. Create User
    await runScenario("Create User", "Create user Maria Souza, dept RH, type Efetivo, matricula 55555. IMPAC: CRITICO");

    // 3. Printer Issue
    await runScenario("Printer Issue", "Printer on 2nd floor is broken. Paper jam. Low Urgency.");
}

verify().catch(console.error);
