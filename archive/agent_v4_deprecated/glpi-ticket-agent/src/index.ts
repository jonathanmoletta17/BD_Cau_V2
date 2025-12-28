import express from 'express';
import cors from 'cors';
import Redis from 'ioredis';
import { RedisSessionRepository } from './repositories/redis_repository';
import { configManager } from './config';
import { GlpiClient } from './services/glpi';
import { llmService } from './services/llm_service';
import { TaxonomyService } from './services/taxonomy';
import dotenv from 'dotenv';
import { GLPIAgentV4 } from './v4/agent';

// Sprint 3: Guardrails
import { ChatInputSchema, createValidationMiddleware } from './v4/schemas/validation';
import { AuditLogger } from './services/audit_logger';
import { RateLimiter, RateLimitPresets } from './middleware/rate_limiter';
import { SafetyService } from './services/safety_service';

// Carregar variáveis de ambiente do .env do monorepo
dotenv.config({ path: '../.env' });
dotenv.config();

const app = express();
const port = process.env.PORT || 4000;

app.use(express.json());
app.use(cors());

const redis = new Redis();
const redisRepo = new RedisSessionRepository(); // RedisSessionRepository cria próprio client
const glpiConfig = configManager.getGlpiConfig();
const glpi = new GlpiClient(glpiConfig);
const taxonomy = new TaxonomyService(glpi);

// V4 Agent com schemas dinâmicos
const v4Agent = new GLPIAgentV4(
  redis,
  llmService,
  {
    baseUrl: glpiConfig.url,
    appToken: glpiConfig.appToken,
    userToken: glpiConfig.userToken || ''
  }
);

// Sprint 3: Inicializar Guardrails
const auditLogger = new AuditLogger(redis);
const rateLimiter = new RateLimiter(redis, RateLimitPresets.MODERATE);
const safetyService = new SafetyService();

console.log('[Guardrails] ✅ Audit, RateLimit e Safety habilitados');

app.get('/health', (req, res) => {
  res.json({ status: 'OK', architecture: 'v4-dynamic-agent' });
});

app.get('/llm-status', (req, res) => {
  const status = llmService.getStatus();
  res.json({
    ...status,
    timestamp: new Date().toISOString()
  });
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
  const startTime = Date.now();

  try {
    const { message, sessionId = 'default', userId = 'unknown', conversationId } = req.body;

    console.log(`[Chat] Incoming: "${message}" from ${userId}`);

    // 🛡️ GUARDRAIL 1: Safety Check
    const safetyCheck = safetyService.validateInput(message || '');
    if (!safetyCheck.isSafe) {
      console.warn(`[Safety] ⚠️ Blocked unsafe message from ${userId}: ${safetyCheck.reason}`);

      // Audit log (bloqueio)
      await auditLogger.log({
        userId,
        action: 'SAFETY_BLOCKED',
        payload: { message: message?.substring(0, 100) },
        result: 'BLOCKED',
        reason: safetyCheck.reason
      });

      return res.status(400).json({
        error: 'Message blocked for safety reasons',
        message: 'Your message was flagged as potentially unsafe. Please rephrase.',
        details: safetyCheck.reason
      });
    }

    // Sanitizar input
    const sanitizedMessage = safetyService.sanitizeInput(message);

    // Random suffix to avoid collisions
    const randomSuffix = Math.random().toString(36).substring(2, 7);
    const convId = conversationId || `conv-${sessionId}-${Date.now()}-${randomSuffix}`;

    // Processar com V4 Agent
    const result = await v4Agent.process(convId, sanitizedMessage, userId);

    // 🛡️ GUARDRAIL 2: Audit Logging (sucesso)
    await auditLogger.log({
      userId,
      action: 'CHAT_MESSAGE',
      intent: result.metadata?.intent,
      payload: {
        message: sanitizedMessage.substring(0, 100),
        sessionId
      },
      result: 'SUCCESS',
      metadata: {
        responseType: result.type,
        processingTime: Date.now() - startTime
      }
    });

    res.json({
      response: result.message,
      conversationId: convId,
      type: result.type,
      metadata: result.metadata,
      architecture: 'V3-Hybrid'
    });

  } catch (error: any) {
    console.error('[Chat] Error:', error);

    // 🛡️ GUARDRAIL 3: Audit Logging (erro)
    const userId = req.body.userId || 'unknown';
    await auditLogger.log({
      userId,
      action: 'ERROR',
      payload: { message: req.body.message?.substring(0, 100) },
      result: 'FAILURE',
      reason: error.message,
      metadata: {
        stack: error.stack?.substring(0, 200)
      }
    });

    res.status(500).json({
      error: 'Internal server error',
      message: 'An error occurred while processing your request'
    });
  }
});

app.post('/chat/submit', async (req, res) => {
  try {
    const { conversationId, formData, userId = 'unknown' } = req.body;
    console.log(`[Form] Submission for ${conversationId} by ${userId} `);

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
    console.log(`[Ticket] Creation Request: `, { title, category });

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
      title: title || `Chamado via IA - ${category || 'Geral'} `,
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

// 🛡️ Endpoint de Auditoria (Sprint 3)
app.get('/audit/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const limit = parseInt(req.query.limit as string || '20');

    const trail = await auditLogger.getUserAuditTrail(userId, limit);
    const stats = await auditLogger.getStats(userId);

    res.json({
      userId,
      events: trail,
      stats,
      count: trail.length
    });
  } catch (error: any) {
    console.error('[Audit] Error:', error);
    res.status(500).json({ error: 'Failed to fetch audit trail' });
  }
});

// 🛡️ Endpoint de Estatísticas Globais
app.get('/audit/stats/global', async (req, res) => {
  try {
    const stats = await auditLogger.getStats();
    const recentEvents = await auditLogger.getRecentEvents(50);

    res.json({
      stats,
      recentEventCount: recentEvents.length,
      lastEvent: recentEvents[0] || null
    });
  } catch (error: any) {
    console.error('[Audit Stats] Error:', error);
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});

app.listen(port, () => {
  console.log(`🚀 Ticket Agent V2 running on port ${port} `);
});
