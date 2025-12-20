
import { TriageGraphConfigDriven } from "../agent/graph";
import * as dotenv from 'dotenv';
dotenv.config();

const MOCK_SYSTEM_INFO = {
    System: { Hostname: "VALIDATION-PC", OS: "Windows 11", Build: "22621" },
    Network: { IP: "10.0.0.99" },
    Hardware: { SerialNumber: "VAL-999" }
};

async function verifyCreateUser() {
    console.log(`\n=================================================`);
    console.log(`🚀 SCENARIO: Create User Validation`);
    console.log(`=================================================`);

    const graph = new TriageGraphConfigDriven();
    const input = "Create user Maria Souza, dept RH, type Efetivo, matricula 55555, CPF 12345678900. IMPACTO CRITICO.";

    let state = await graph.process(input, undefined, MOCK_SYSTEM_INFO);
    console.log(`\n👤 User: "${input}"`);

    if (!state.is_complete && state.messages.length > 0) {
        const lastMsg = state.messages[state.messages.length - 1];
        if (lastMsg.role === 'agent') {
            console.log(`\n🤖 Agent Asks: ${lastMsg.content.substring(0, 150)}...`);

            const reply = "Meu ramal é 4321";
            console.log(`\n👤 User (Simulated): "${reply}"`);
            state = await graph.process(reply, state);
        }
    }

    if (state.is_complete) {
        console.log(`✅ TICKET COMPLETE!`);
        console.log(`   Internal Sub-Intent: ${state.intent}`);
        console.log(`   FINAL PAYLOAD:`, JSON.stringify(state.ticket_payload, null, 2));

        const sysMsg = state.messages.find(m => m.content.includes("(SYSTEM) Mapped"));
        if (sysMsg) {
            console.log(`\n   GLPI Result: ${sysMsg.content}`);
        } else {
            console.log(`\n   ⚠️ WARNING: GLPI Mapping message not found.`);
        }
    } else {
        console.log(`🛑 FAILED to complete scenario.`);
        console.log(`   Last Msg: ${state.messages[state.messages.length - 1].content}`);
    }
}

verifyCreateUser().catch(console.error);
