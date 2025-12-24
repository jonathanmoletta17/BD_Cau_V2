import { Redis } from 'ioredis';
import { LLMService } from '../services/llm_service';
import { RouterService } from './orchestrator/router';
import { FormAgentV4 } from './agents/form_agent_v4';
import { IncidentAgent } from './agents/incident_agent';
import { GLPIBridgeService } from './services/glpi_bridge_service';
import { AgentResponse, V3Intent } from './types';
import { ConversationStateManager } from './state/conversation_state';

/**
 * GLPIAgentV4 - Orquestrador principal com schemas dinâmicos
 * 
 * Diferenças da V3:
 * - Usa GLPIBridgeService para buscar metadados reais do GLPI
 * - FormAgent gera schemas dinamicamente (não usa create_user.ts)
 * - Cache inteligente (10min) para performance
 */
export class GLPIAgentV4 {
    private router: RouterService;
    private formAgent: FormAgentV4;
    private incidentAgent: IncidentAgent;
    private glpiBridge: GLPIBridgeService;

    constructor(
        private redis: Redis,
        private llm: LLMService,
        glpiConfig: {
            baseUrl: string;
            appToken: string;
            userToken: string;
        }
    ) {
        // Inicializa a ponte GLPI
        this.glpiBridge = new GLPIBridgeService(
            glpiConfig.baseUrl,
            glpiConfig.appToken,
            glpiConfig.userToken,
            redis
        );

        // Inicializa agentes
        const stateManager = new ConversationStateManager(redis);
        this.router = new RouterService(llm);
        this.formAgent = new FormAgentV4(llm, this.glpiBridge);
        this.incidentAgent = new IncidentAgent(llm, stateManager);

        console.log('[V4] GLPI Agent Inicializado com schemas dinâmicos 🚀');
    }

    async process(conversationId: string, message: string, userId: string): Promise<AgentResponse> {
        console.log(`[V4] Processando: "${message}" (User: ${userId})`);

        // 1. Carregar estado do Redis
        const stateKey = `v4:state:${conversationId}`;
        const rawState = await this.redis.get(stateKey);
        const state = rawState ? JSON.parse(rawState) : { history: [], lastIntent: null };

        state.history.push({ role: 'user', content: message });

        // 2. Classificar Intent (com viés de contexto)
        let intent: V3Intent = 'UNKNOWN';

        if (state.lastIntent === 'INCIDENT') {
            intent = 'INCIDENT';
            console.log(`[V4] Continuação de contexto: permanece em INCIDENT`);
        } else {
            intent = await this.router.classify(message, state.history.map((h: any) => h.content));
        }

        console.log(`[V4] Decisão do Router: ${intent}`);

        // Atualizar estado
        if (intent !== 'UNKNOWN' && intent !== 'CHITCHAT') {
            state.lastIntent = intent;
        }

        // 3. Despachar para o agente apropriado
        let response: AgentResponse;

        console.log('[V4] 🎯 About to switch, intent =', intent, '| type:', typeof intent);

        switch (intent) {
            case 'SERVICE_REQUEST':
                // Usa FormAgentV4 (dinâmico!)
                response = await this.formAgent.process(
                    message,
                    state.history.map((h: any) => h.content)
                );
                break;

            case 'INCIDENT':
                console.log('[V4] 🔧 Executing INCIDENT case, calling IncidentAgent...');
                // IncidentAgent (mantém lógica V3 por enquanto)
                response = await this.incidentAgent.process(
                    message,
                    state.history.map((h: any) => h.content),
                    conversationId
                );
                console.log('[V4] 📤 IncidentAgent returned:', { hasMessage: !!response?.message, type: response?.type });
                break;

            case 'CHITCHAT':
                response = {
                    type: 'TEXT',
                    message: "Olá! Como posso ajudar com seus chamados hoje?",
                    metadata: { intent: 'CHITCHAT' }
                };
                break;

            default:
                response = {
                    type: 'TEXT',
                    message: "Desculpe, não entendi o que você precisa. Pode detalhar melhor?",
                    metadata: { intent: 'UNKNOWN' }
                };
        }

        // 4. Salvar estado + histórico
        console.log('[V4] 💾 Response before save:', JSON.stringify(response).substring(0, 200));
        state.history.push({ role: 'assistant', content: response.message });
        if (state.history.length > 20) state.history = state.history.slice(-20);

        await this.redis.set(stateKey, JSON.stringify(state), 'EX', 3600);

        return response;
    }

    async handleFormSubmit(conversationId: string, formData: any, userId: string): Promise<AgentResponse> {
        console.log(`[V4] Submissão de formulário de ${userId}:`, formData);

        // Mock de criação de ticket (em produção, usar GLPI API)
        const ticketId = Math.floor(Math.random() * 10000) + 5000;

        return {
            type: 'TEXT',
            message: `✅ **Sucesso!** O ticket **#${ticketId}** foi criado para: **${formData.userName}**.\n\nVocê receberá atualizações por e-mail.`,
            metadata: {
                ticketId: ticketId.toString()
            }
        };
    }

    /**
     * Limpa recursos ao desligar
     */
    async shutdown(): Promise<void> {
        await this.glpiBridge.close();
        console.log('[V4] Agente desligado');
    }
}
