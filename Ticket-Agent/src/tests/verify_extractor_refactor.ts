import { ExtractorConfigDriven } from "../agent/extractor";

async function verify() {
    const extractor = new ExtractorConfigDriven();
    console.log("Starting Extractor Verification...");

    // Case 1: Create User Efetivo
    // Keywords in inference_rules.json: "Efetivo": ["efetivo", ...]
    console.log("\n--- Case 1: Create User Efetivo ---");
    const text1 = "Novo usuario efetivo para o Carlos Silva no RH";
    const payload1 = await extractor.extract(text1, "CREATE_USER");
    console.log(`Input: "${text1}"`);
    console.log("Payload:", payload1);

    if (payload1.user_type === 'Efetivo') {
        console.log("✅ User Type detected via Keywords");
    } else {
        console.error("❌ User Type detection failed");
    }
    if (payload1.full_name === 'Carlos Silva' || payload1.full_name?.includes('Carlos')) {
        console.log("✅ Full Name detected (likely via LLM)");
    }
    if (payload1.department === 'RH') {
        console.log("✅ Department detected (likely via LLM)");
    }

    // Case 2: Equipment Request
    // Keywords: "mouse"
    console.log("\n--- Case 2: Equipment Reference ---");
    const text2 = "Meu mouse quebrou";
    const payload2 = await extractor.extract(text2, "EQUIPMENT_REQUEST");
    console.log(`Input: "${text2}"`);
    console.log("Payload:", payload2);

    if (payload2.item === 'mouse') {
        console.log("✅ Item detected via Simple Keywords");
    } else {
        console.error("❌ Item detection failed");
    }

    // Case 3: VPN Access
    // Keywords: "instalar" -> "Install_Client"
    console.log("\n--- Case 3: VPN Install ---");
    const text3 = "Instalar vpn urgente";
    const payload3 = await extractor.extract(text3, "VPN_ACCESS");
    console.log(`Input: "${text3}"`);
    console.log("Payload:", payload3);

    if (payload3.action === 'Install_Client') {
        console.log("✅ Action detected via Enum Keywords");
    } else {
        console.error("❌ Action detection failed");
    }

    // Case 4: CPF Pattern
    console.log("\n--- Case 4: CPF Pattern matching ---");
    const text4 = "CPF 123.456.789-00";
    const payload4 = await extractor.extract(text4, "CREATE_USER");
    console.log(`Input: "${text4}"`);
    console.log("Payload:", payload4);

    if (payload4.cpf === '123.456.789-00') {
        console.log("✅ CPF Pattern matched");
    } else {
        console.error("❌ CPF Pattern failed");
    }

    // Case 5: Third Party (Negative Test)
    // "Novo usuario terceiro" -> Should NOT have user_type="Terceiro"
    console.log("\n--- Case 5: Third Party (Negative) ---");
    const text5 = "Novo usuario terceiro";
    const payload5 = await extractor.extract(text5, "CREATE_USER");
    console.log(`Input: "${text5}"`);
    console.log("Payload:", payload5);

    if (payload5.user_type !== 'Terceiro') {
        console.log("✅ Terceiro NOT detected (Correct)");
    } else {
        console.error("❌ Terceiro DETECTED (Governance Violation)");
    }

}

verify().catch(console.error);
