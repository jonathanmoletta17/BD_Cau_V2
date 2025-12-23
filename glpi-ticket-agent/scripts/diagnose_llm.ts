
import fetch from 'node-fetch';

const BASE_URL = 'http://127.0.0.1:11434';
const MODEL = 'llama3.1';

async function diagnose() {
    console.log(`🔍 Diagnosing LLM connection at ${BASE_URL}...`);

    // 1. Check Connectivity
    try {
        const res = await fetch(`${BASE_URL}/api/tags`);
        if (!res.ok) {
            console.error(`❌ Connection Established but endpoint failed: ${res.status}`);
            return;
        }
        const data: any = await res.json();
        console.log("✅ Connectivity: OK");

        // 2. Check Model
        const models = data.models || [];
        const modelExists = models.find((m: any) => m.name.includes(MODEL) || m.model?.includes(MODEL));

        if (modelExists) {
            console.log(`✅ Model '${MODEL}' found.`);
        } else {
            console.error(`❌ Model '${MODEL}' NOT found. Available models:`);
            console.log(models.map((m: any) => m.name));
            console.log("\n!!! You must run 'ollama pull llama3.1' !!!");
        }

    } catch (e: any) {
        console.error(`❌ Connection Failed: ${e.message}`);
        console.error("Is Ollama running? (Try 'systemctl status ollama' or just 'ollama serve')");
    }
}

diagnose();
