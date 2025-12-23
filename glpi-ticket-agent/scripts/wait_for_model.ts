
import fetch from 'node-fetch';

const BASE_URL = 'http://127.0.0.1:11434';
const MODEL = 'llama3.1';

async function wait() {
    process.stdout.write(`⏳ Waiting for model '${MODEL}'...`);

    while (true) {
        try {
            const res = await fetch(`${BASE_URL}/api/tags`);
            if (res.ok) {
                const data: any = await res.json();
                const exists = data.models?.find((m: any) => m.name.includes(MODEL));
                if (exists) {
                    console.log("\n✅ Model Ready!");
                    process.exit(0);
                }
            }
        } catch (e) { }

        process.stdout.write(".");
        await new Promise(r => setTimeout(r, 5000));
    }
}

wait();
