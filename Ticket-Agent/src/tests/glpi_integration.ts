
import { GlpiClient } from '../services/glpi';
import { GlpiConfig } from '../agent/config_loader';
import { EdgeCaseTicket } from '../services/edge_case_generator';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load env vars
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../../../../.env') });

async function runIntegrationTests() {
    console.log("=== GLPI Integration Tests (Edge Cases) ===");

    // Load edge cases
    const casesPath = path.resolve(__dirname, '../../data/edge_cases.json');
    if (!fs.existsSync(casesPath)) {
        console.error("Error: edge_cases.json not found. Run scripts/generate_edge_cases.ts first.");
        return;
    }
    const edgeCases: EdgeCaseTicket[] = JSON.parse(fs.readFileSync(casesPath, 'utf-8'));
    console.log(`Loaded ${edgeCases.length} edge cases.`);

    // Initialize Client with TEST config from usage of .env
    const glpiConfig: GlpiConfig = {
        url: process.env.GLPI_TEST_URL_CONFIG || "",
        userToken: process.env.GLPI_TEST_USER_TOKEN || "",
        appToken: process.env.GLPI_TEST_APP_TOKEN || "",
        isReadOnly: false // Explicitly false for testing ticket creation
    };

    if (!glpiConfig.url || (!glpiConfig.userToken && (!glpiConfig.username || !glpiConfig.password))) {
        console.warn("Usage: Ensure GLPI_TEST_URL_CONFIG, GLPI_TEST_USER_TOKEN (or GLPI_TEST_USERNAME/PASSWORD), and GLPI_TEST_APP_TOKEN are set in .env");
    }

    const client = new GlpiClient(glpiConfig);

    try {
        console.log(`Connecting to GLPI TEST at ${glpiConfig.url}...`);
        await client.initSession();
        console.log("Connection successful!");
    } catch (error: any) {
        console.error("FATAL: Could not connect to GLPI TEST.");
        console.error("Reason:", error.message);
        console.log("Skipping actual test execution due to connection failure.");
        console.log("Please verify the GLPI_TEST_* variables in .env");
        return;
    }

    // Execute Tests
    let passed = 0;
    let failed = 0;

    for (const testCase of edgeCases) {
        console.log(`\n-- - Running Case: ${testCase.description_scenario} --- `);
        try {
            // Note: createTicket signature is (title, content, urgency). 
            // If we need to pass category_id, we might need to update createTicket or pass it in payload.
            // For now, using the simple signature.
            // TODO: Update GlpiClient to support category assignment if needed.

            const result = await client.createTicket(testCase.name, testCase.content, testCase.urgency);
            console.log(`RESULT: Created Ticket ID ${result.id} `);
            passed++;
        } catch (error: any) {
            console.log(`RESULT: Failed(Expected ? Maybe).Error: ${error.message} `);
            // We might want to assert specific errors for specific cases (e.g. invalid category)
            failed++;
        }
    }

    console.log(`\n === Summary === `);
    console.log(`Total: ${edgeCases.length} `);
    console.log(`Passed(Created): ${passed} `);
    console.log(`Failed(Error): ${failed} `);

    await client.killSession();
}

runIntegrationTests();
