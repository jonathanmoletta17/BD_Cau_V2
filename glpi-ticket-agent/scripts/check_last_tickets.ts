
import { configManager } from '../src/config';
import { GlpiClient } from '../src/services/glpi';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '../.env') });

async function checkRecentTickets() {
    const config = configManager.getGlpiConfig();
    const glpi = new GlpiClient(config);

    try {
        await glpi.initSession();
        console.log("Session Initialized.");

        // Fetch last 5 tickets
        // GLPI sort order usually requires criteria, but default list often sorts by ID desc or asc.
        // We'll try to fetch a range and see.
        // Or usage of order parameter: sort=id&order=DESC
        const tickets = await glpi.request('Ticket', 'GET', {
            range: '0-5',
            sort: 'id',
            order: 'DESC'
        });

        console.log("\n--- Last 5 Tickets ---");
        tickets.forEach((t: any) => {
            console.log(`[${t.id}] ${t.name} (Category: ${t.itilcategories_id}) - Date: ${t.date}`);
            // verify content briefly
            console.log(`     Desc: ${t.content.replace(/\n/g, ' ').substring(0, 50)}...`);
        });

    } catch (e: any) {
        console.error("Error:", e.message);
    } finally {
        await glpi.killSession();
    }
}

checkRecentTickets();
