
import readline from 'readline';
import fetch from 'node-fetch';

const AGENT_URL = 'http://localhost:8000/chat';
const SESSION_ID = 'cli-user-' + Math.floor(Math.random() * 1000);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

console.log(`
=============================================
🤖 Ticket Agent CLI (Session: ${SESSION_ID})
=============================================
Type your message and press Enter.
Type 'exit' to quit.
---------------------------------------------
`);

async function ask(question: string) {
    rl.question(`You: `, async (input) => {
        if (input.toLowerCase() === 'exit') {
            rl.close();
            return;
        }

        try {
            // For testing Asset Lookup, we can inject a mock IP
            // Or remove it to test 'Not Found' / 'Localhost' logic
            const payload = {
                message: input,
                sessionId: SESSION_ID,
                mockIp: "10.72.16.203" // Optional: Uncomment to simulate the Asset PC
            };

            const res = await fetch(AGENT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                console.log(`\nServer Error: ${res.statusText}\n`);
            } else {
                const data: any = await res.json();
                console.log(`\nAgent:\n${data.response}\n`);
            }

        } catch (e: any) {
            console.error(`\nConnection Error: Is the server running? (${e.message})\n`);
        }

        ask("");
    });
}

// Start
ask("");
