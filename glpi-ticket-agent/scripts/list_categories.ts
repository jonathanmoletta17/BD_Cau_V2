
import { configManager } from '../src/config';
import { GlpiClient } from '../src/services/glpi';
import dotenv from 'dotenv';
import path from 'path';

// Load Env from Root
dotenv.config({ path: path.resolve(process.cwd(), '../.env') });

async function listCategories() {
    const config = configManager.getGlpiConfig();
    console.log("Config:", { url: config.url, appToken: config.appToken, userToken: config.userToken ? '***' : 'MISSING' });

    const glpi = new GlpiClient(config);

    try {
        await glpi.initSession();
        console.log("Session Initialized. Fetching Categories...");

        // ITILCategory is the endpoint
        const categories = await glpi.listItems('ITILCategory', '0-100');

        console.log("\n--- Categories Found ---");
        categories.forEach((c: any) => {
            console.log(`[${c.id}] ${c.name} (Completo: ${c.completename})`);
        });

    } catch (e: any) {
        console.error("Error:", e.message);
        if (e.response) console.error(await e.response.text());
    } finally {
        await glpi.killSession();
    }
}

listCategories();
