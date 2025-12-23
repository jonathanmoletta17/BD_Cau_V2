
import express from 'express';
import cors from 'cors';
import { RedisSessionRepository } from './repositories/redis_repository';
import { configManager } from './config';
import { GlpiClient } from './services/glpi';
import { llmService } from './services/llm_service';
import { TaxonomyService } from './services/taxonomy';
import dotenv from 'dotenv';
import { GLPIAgentV4 } from './v4/agent';

dotenv.config();

const app = express();
const port = process.env.PORT || 4000;

app.use(express.json());
app.use(cors());

const redisRepo = new RedisSessionRepository();
const glpi = new GlpiClient(configManager.getGlpiConfig());
const taxonomy = new TaxonomyService(glpi);

// V4 Agent com schemas dinâmicos
const v4Agent = new GLPIAgentV4(
  redisRepo.client,
  llmService,
  {
    baseUrl: process.env.GLPI_PROD_URL_CONFIG || '',
    appToken: process.env.GLPI_PROD_APP_TOKEN || '',
    userToken: process.env.GLPI_PROD_USER_TOKEN || ''
  }
);

app.get('/health', (req, res) => {
  res.json({ status: 'OK', architecture: 'v4-dynamic-agent' });
});

app.post('/login', async (req, res) => {
  // ... (keep login as is)
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ error: "Username and Password required" });
    }
    const authData = await glpi.login(username, password);
    res.json({
      success: true,
      userId: authData.userId,
      token: authData.token,
      message: "Login Successful"
    });
  } catch (e: any) {
    console.error("Login Error:", e);
    res.status(401).json({ error: "Authentication Failed", details: e.message });
  }
});

app.post('/chat', async (req, res) => {
  try {
    const { message, sessionId = 'default', userId = 'unknown', conversationId } = req.body;
    console.log(`[Chat] Incoming: "${message}" from ${userId}`);

    // Random suffix to avoid collisions
    const randomSuffix = Math.random().toString(36).substring(2, 7);
    const convId = conversationId || `conv-${sessionId}-${Date.now()}-${randomSuffix}`;

    // V3 Process
    const result = await v4Agent.process(convId, message, userId);

    res.json({
      response: result.message, // Map 'message' to 'response' for frontend compat
      conversationId: convId,
      // V3 specific fields
      type: result.type,
      metadata: result.metadata,
      architecture: 'V3-Hybrid'
    });
  } catch (e: any) {
    console.error("Engine Error:", e);
    res.status(500).json({ error: e.message });
  }
});

app.post('/chat/submit', async (req, res) => {
  try {
    const { conversationId, formData, userId = 'unknown' } = req.body;
    console.log(`[Form] Submission for ${conversationId} by ${userId}`);

    const result = await v4Agent.handleFormSubmit(conversationId, formData, userId);

    res.json({
      response: result.message,
      type: result.type,
      metadata: result.metadata
    });
  } catch (e: any) {
    console.error("Submission Error:", e);
    res.status(500).json({ error: e.message });
  }
});

app.post('/tickets', async (req, res) => {
  try {
    const { userId, title, description, category, location, extension } = req.body;
    console.log(`[Ticket] Creation Request:`, { title, category });

    if (!description || !userId) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    const categoryId = await taxonomy.resolveCategory(category);

    const fullContent = `
Local: ${location || "N/A"}
Ramal: ${extension || "N/A"}

Descrição:
${description}

[Criado via Agente IA]`.trim();

    const ticketId = await glpi.createTicket({
      title: title || `Chamado via IA - ${category || 'Geral'}`,
      content: fullContent,
      _users_id_requester: userId,
      itilcategories_id: categoryId,
      urgency: 3
    });

    res.json({ success: true, ticketId });
  } catch (e: any) {
    console.error("Ticket Creation Error:", e);
    res.status(500).json({ error: e.message });
  }
});

app.listen(port, () => {
  console.log(`🚀 Ticket Agent V2 running on port ${port}`);
});
