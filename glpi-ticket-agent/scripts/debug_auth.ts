
import { GlpiClient } from '../src/services/glpi';
import { configManager } from '../src/config';
import readline from 'readline';

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

async function debugAuth() {
    console.log("🛠️  GLPI Auth Debugger");
    const config = configManager.getGlpiConfig();
    console.log(`Target: ${config.url}`);
    console.log(`App Token: ${config.appToken.substring(0, 5)}...`);

    rl.question('Username: ', (user) => {
        rl.question('Password: ', async (pass) => {
            const client = new GlpiClient(config);
            try {
                console.log("\nAttempting Login...");
                const res = await client.login(user, pass);
                console.log("✅ Success!");
                console.log(res);
            } catch (e: any) {
                console.error("\n❌ Failure Details:");
                console.error(e.message);
                // The error message from GlpiClient already includes the response text.
            }
            rl.close();
            process.exit(0);
        });
    });
}

debugAuth();
