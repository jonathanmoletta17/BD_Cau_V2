
import express from 'express';
import cors from 'cors'; // Need CORS for frontend
import { AgentEngine } from './core/engine';
import { RedisSessionRepository } from './repositories/redis_repository';
import { configManager } from './config';
import { GlpiClient } from './services/glpi';
import { ExtractorService } from './skills/extractor';
import { llmService } from './services/llm_service';
import { TaxonomyService } from './services/taxonomy';

const app = express();
const port = process.env.PORT || 8000;

app.use(express.json());
app.use(cors()); // Allow Frontend to connect

// Initialize Core Dependencies
const redisRepo = new RedisSessionRepository();
const extractor = new ExtractorService(llmService);
const glpi = new GlpiClient(configManager.getGlpiConfig());
const taxonomy = new TaxonomyService(glpi); // Initialize Taxonomy

const engine = new AgentEngine({
  persistence: redisRepo,
  extractor: extractor
});

// --- ROUTES ---

app.get('/health', (req, res) => {
  res.json({ status: 'OK', architecture: 'v2-redis-llm-extracted' });
});

/**
 * Endpoint for Frontend Authentication (Gateway Pattern)
 * The frontend calls this to get a valid UserID and SessionToken from GLPI.
 */
app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ error: "Username and Password required" });
    }

    // Authenticate against GLPI
    const authData = await glpi.login(username, password);

    // Return the user identity to the frontend
    res.json({
      success: true,
      userId: authData.userId,
      token: authData.token, // GLPI Session Token
      message: "Login Successful"
    });
  } catch (e: any) {
    console.error("Login Error:", e);
    res.status(401).json({ error: "Authentication Failed", details: e.message });
  }
});

/**
 * Main Chat Endpoint
 * Receives message, returns Text Response AND Semantic Entities.
 */
app.post('/chat', async (req, res) => {
  try {
    const { message, sessionId = 'default', userId = 'unknown' } = req.body;

    console.log(`[Chat] Incoming: "${message}" from ${userId}`);

    // The Engine now returns { response, data }
    const result = await engine.process(sessionId, message, userId);

    res.json({
      response: result.response,
      entities: result.data, // Semantic Entities for Sidebar
      type: 'MESSAGE'
    });
  } catch (e: any) {
    console.error("Engine Error:", e);
    res.status(500).json({ error: e.message });
  }
});

/**
 * Direct Ticket Creation Endpoint (From Sidebar)
 */
app.post('/tickets', async (req, res) => {
  try {
    const { userId, title, description, category, location, extension } = req.body;

    console.log(`[Ticket] Creation Request from User ${userId}:`, { title, category });

    // Validation
    if (!description || !userId) {
      return res.status(400).json({ error: "Missing required fields (description, userId)" });
    }

    // Dynamic Category Resolution
    const categoryId = await taxonomy.resolveCategory(category);
    console.log(`[Ticket] Resolved Category '${category}' -> ID ${categoryId}`);

    // Construct Content
    const fullContent = `
Local: ${location || "N/A"}
Ramal: ${extension || "N/A"}

Descrição:
${description}

[Criado via Agente IA]
    `.trim();

    const ticketId = await glpi.createTicket({
      title: title || `Chamado via IA - ${category || 'Geral'}`,
      content: fullContent,
      _users_id_requester: userId,
      itilcategories_id: categoryId,
      urgency: 3 // Medium default
    });

    res.json({ success: true, ticketId });

  } catch (e: any) {
    console.error("Ticket Creation Error:", e);
    res.status(500).json({ error: e.message });
  }
});


app.listen(port, () => {
  console.log(`🚀 Ticket Agent V2 (Full Stack Ready) running on port ${port}`);
});
