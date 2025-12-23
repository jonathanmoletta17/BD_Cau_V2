
import express, { Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { TriageGraphConfigDriven } from './agent/graph';
import { type AgentState } from './agent/schema';

const app = express();
const port = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());

// Serve Static Frontend (REMOVED)
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);
// const frontendPath = path.join(__dirname, '../frontend/dist');

// Middleware to serve static files
// app.use(express.static(frontendPath));

// Initialize the Graph
const graph = new TriageGraphConfigDriven();

// In-memory state store (simple Map to handle sessions for basic persistence)
const sessions = new Map<string, AgentState>();

/**
 * Chat Endpoint
 * POST /chat
 * Body: { message: string, sessionId?: string, systemInfo?: any }
 */
app.post('/chat', async (req: Request, res: Response) => {
  try {
    const { message, sessionId = 'default', systemInfo } = req.body;

    if (!message) {
      res.status(400).json({ error: "Message is required" });
      return;
    }

    console.log(`[Request] Session: ${sessionId} | Message: ${message}`);

    // Retrieve or initialize state
    let currentState = sessions.get(sessionId);

    // Process message through Agent Graph
    const newState = await graph.process(message, currentState, systemInfo);

    // Update Session
    sessions.set(sessionId, newState);

    // Extract last agent message
    const lastMessage = newState.messages[newState.messages.length - 1];
    const responseText = (lastMessage && lastMessage.role === 'agent') ? lastMessage.content : "";

    // Send Response
    res.json({
      response: responseText,
      state: {
        intent: newState.intent,
        is_complete: newState.is_complete,
        missing_fields: newState.missing_fields,
        ticket_payload: newState.ticket_payload,
        diagnostics: newState.diagnostics
      }
    });

  } catch (error: any) {
    console.error("Error processing request:", error);
    res.status(500).json({ error: error.message || "Internal Server Error" });
  }
});

/**
 * Health Check
 * GET /health
 */
app.get('/health', (req, res) => {
  res.json({ status: "ok", agent: "Ticket-Agent V2" });
});

// SPA Fallback - Serve index.html for any unknown route (REMOVED)
// app.get(/.*/, (req: Request, res: Response) => {
//   ...
// });

// Start Server
app.listen(port, () => {
  console.log(`🚀 Ticket Agent V2 API running on port ${port}`);
});
