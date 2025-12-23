import { ExtractorConfigDriven } from "../agent/extractor";

async function verify() {
    const extractor = new ExtractorConfigDriven();
    console.log("Starting Final Verification...");

    // Case 6: Printer Issue with Location
    console.log("\n--- Case 6: Printer Issue Location ---");
    const text6 = "A impressora da contabilidade não imprime";
    const payload6 = await extractor.extract(text6, "PRINTER_ISSUE");
    console.log(`Input: "${text6}"`);
    console.log("Payload:", payload6);

    if (payload6.location && payload6.location.toLowerCase().includes('contabilidade')) {
        console.log("✅ Location detected (likely via LLM)");
    } else {
        console.warn("⚠️ Location NOT detected. (LLM might fail on short text or not configured to extract 'location' specifically if not in schema?)");
        // Note: Extractor logic uses schema fields to prompt LLM. So adding 'location' to schema helps.
    }

}

verify().catch(console.error);
