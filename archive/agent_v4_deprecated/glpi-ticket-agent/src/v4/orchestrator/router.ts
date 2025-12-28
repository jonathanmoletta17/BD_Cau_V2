
import { LLMService } from '../../services/llm_service';
import { RAGService } from '../services/rag_service';
import { TelemetryService } from '../services/telemetry_service';
import { V3Intent } from '../types';

export class RouterService {
    private ragService: RAGService;

    constructor(
        private llm: LLMService,
        private telemetry?: TelemetryService
    ) {
        this.ragService = new RAGService();
    }

    async classify(message: string, history: string[], conversationId?: string): Promise<V3Intent> {
        // Iniciar telemetria
        const telemetryEvent = conversationId && this.telemetry
            ? this.telemetry.createEvent(conversationId, 'Router', 'classification')
            : null;

        // Obter exemplos de classificação do RAG
        const examples = this.ragService.getClassificationExamples();

        const systemPrompt = `
Você é o Orquestrador de um Agente de Suporte de TI.
Classifique a MENSAGEM DO USUÁRIO em uma destas categorias:

1. **SERVICE_REQUEST**: Usuário quer criar/configurar/adicionar algo (AÇÃO DIRETA).
   ✅ Exemplos VÁLIDOS:
   - "Criar usuário para João"
   - "Preciso de acesso para Maria"
   - "Usuário para Pedro da SECOM" ← IMPLÍCITO mas É SERVICE_REQUEST
   - "João precisa de conta"
   - "Adicionar Ana no sistema"
   - "Configurar VPN para equipe" ← AÇÃO (fazer algo)
   
   ❌ NÃO é SERVICE_REQUEST:
   - Algo quebrado/não funciona
   - PERGUNTAS sobre como fazer algo

2. **INCIDENT**: Algo está QUEBRADO ou NÃO FUNCIONANDO.
   ✅ Exemplos:
   - "Impressora não imprime"
   - "Internet lenta"
   - "Não consigo logar"
   - "Sistema travou"
   - "Esqueci minha senha" ← INCIDENT (problema de acesso)
   - "Senha não funciona"
   
3. **CHITCHAT**: Saudações, agradecimentos, PERGUNTAS DE AJUDA/ORIENTAÇÃO.
   ✅ Exemplos:
   - "Oi", "Olá", "Obrigado"
   - "Como faço para configurar VPN?" ← PERGUNTA (quer aprender)
   - "Como criar um usuário?" ← PERGUNTA (quer instruções)
   - "O que é reset de senha?"
   - "Qual o procedimento de backup?"
   - "Onde encontro o manual?"
   - "Preciso de ajuda"
   - "Como funciona o sistema?"
   
   🔑 DIFERENÇA CRÍTICA:
   - "Como criar usuário?" = CHITCHAT (PERGUNTA - quer saber como)
   - "Criar usuário para João" = SERVICE_REQUEST (AÇÃO - quer que faça)

${examples}

⚠️ IMPORTANTE: 
- PERGUNTAS iniciando com "Como", "O que", "Qual", "Onde" → CHITCHAT
- Se menciona "usuário", "acesso", "criar", "adicionar" MAS é pergunta → CHITCHAT
- Se menciona "esqueci senha", "não funciona", "quebrou" → INCIDENT
- "Esqueci senha" é INCIDENT (não é criar algo novo)

Retorne APENAS o nome da categoria.
        `.trim();

        try {
            const response = await this.llm.complete(message, systemPrompt);
            console.log(`[Router] Raw Response: "${response}"`);

            // Robust validation using Regex
            const normalized = response.toUpperCase();
            let intent: V3Intent = 'UNKNOWN';

            if (normalized.includes('SERVICE_REQUEST') || normalized.includes('SERVICE')) intent = 'SERVICE_REQUEST';
            else if (normalized.includes('INCIDENT')) intent = 'INCIDENT';
            else if (normalized.includes('CHITCHAT')) intent = 'CHITCHAT';
            let llmConfidence = 0.5;

            if (this.isValidIntent(response)) {
                const normalized = response.toUpperCase();
                if (normalized.includes('SERVICE_REQUEST') || normalized.includes('SERVICE')) intent = 'SERVICE_REQUEST';
                else if (normalized.includes('INCIDENT')) intent = 'INCIDENT';
                else if (normalized.includes('CHITCHAT')) intent = 'CHITCHAT';
                llmConfidence = 0.95;
            } else {
                console.warn(`[Router] LLM returned invalid intent: "${response}". Falling back to keyword classification.`);
                intent = this.fallbackClassification(message);
                llmConfidence = 0.6; // Lower confidence for fallback
            }

            console.log(`[Router] Mapped Intent: ${intent}`);

            // Detectar keywords para telemetria
            const keywords_found: string[] = [];
            if (message.toLowerCase().includes('criar')) keywords_found.push('criar');
            if (message.toLowerCase().includes('usuário') || message.toLowerCase().includes('usuario')) keywords_found.push('usuário');
            if (message.toLowerCase().includes('impressora')) keywords_found.push('impressora');
            if (message.toLowerCase().includes('senha')) keywords_found.push('senha');

            // Completar telemetria
            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: intent,
                    confidence: llmConfidence,
                    reasoning: {
                        keywords_found,
                        llm_raw_response: response
                    }
                });
            }

            return intent;

        } catch (error) {
            console.error('[Router] LLM failed, using keyword fallback:', error);

            // NOVO: Fallback baseado em keywords
            const fallbackIntent = this.fallbackClassification(message);

            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: fallbackIntent,
                    confidence: 0.6,
                    reasoning: {
                        fallback_used: true,
                        error: String(error)
                    }
                });
            }

            return fallbackIntent;
        }
    }

    /**
     * NOVO: Fallback classification baseado em keywords
     * Usado quando LLM falha ou retorna resposta inválida
     */
    private fallbackClassification(message: string): V3Intent {
        const lower = message.toLowerCase();

        // PRIORIDADE 1: Perguntas de ajuda/orientação
        // "Como faço para...", "O que é...", "Qual o procedimento..."
        const helpQuestionPatterns = [
            /^(como|o que|qual|onde|quando|por que|porque)\s+(faço|faz|fazer|é|são|posso|devo|deve)/i,
            /\b(como|qual|donde)\s+(criar|resetar|configurar|acessar|instalar|usar|funciona)/i,
            /\b(ajuda|tutorial|guia|manual|instrução|instruções|orientação)\b/i,
            /\bpreciso\s+de\s+ajuda\b/i
        ];

        for (const pattern of helpQuestionPatterns) {
            if (pattern.test(lower)) {
                console.log('[Router] Fallback matched: CHITCHAT (help question)');
                return 'CHITCHAT';
            }
        }

        // SERVICE_REQUEST patterns (ordem importa!)
        const servicePatterns = [
            /\b(criar|novo|adicionar|precis[ao])\s+(usuário|usuario|conta|acesso|login)\b/i,
            /\busuário\s+para\b/i,
            /\bacesso\s+para\b/i,
            /\bcriar\s+\w+\s+(para|da|do|na|no)\b/i,
            /\bprecis[ao]\s+de\s+(usuário|usuario|conta|acesso)\b/i
        ];

        for (const pattern of servicePatterns) {
            if (pattern.test(lower)) {
                console.log('[Router] Fallback matched: SERVICE_REQUEST');
                return 'SERVICE_REQUEST';
            }
        }

        // INCIDENT patterns
        const incidentPatterns = [
            /\bnão\s+(funciona|imprime|conecta|abre|carrega)\b/i,
            /\b(problema|erro|falha|quebr[ou|ada]|travou)\b/i,
            /\b(lento|lenta|devagar)\b/i,
            /\besqueci\s+(minha\s+)?senha\b/i,
            /\bsenha\s+não\s+funciona\b/i,
            /\b(impressora|internet|email|sistema|computador).*(não|problema|erro)\b/i
        ];

        for (const pattern of incidentPatterns) {
            if (pattern.test(lower)) {
                console.log('[Router] Fallback matched: INCIDENT');
                return 'INCIDENT';
            }
        }

        // CHITCHAT patterns
        const chitchatPatterns = [
            /^(oi|olá|ola|hey|hello|bom\s+dia|boa\s+tarde|boa\s+noite)/i,
            /^(obrigad[oa]|valeu|thanks)/i,
            /^(tchau|até|bye|falou)/i,
            /\b(você\s+é|quem\s+é\s+você|o\s+que\s+você)\b/i
        ];

        for (const pattern of chitchatPatterns) {
            if (pattern.test(lower)) {
                console.log('[Router] Fallback matched: CHITCHAT');
                return 'CHITCHAT';
            }
        }

        console.log('[Router] Fallback: UNKNOWN (no patterns matched)');
        return 'UNKNOWN';
    }

    /**
     * NOVO: Verifica se resposta do LLM é válida
     */
    private isValidIntent(response: string): boolean {
        const valid = ['SERVICE_REQUEST', 'INCIDENT', 'CHITCHAT', 'UNKNOWN'];
        return valid.some(intent => response.toUpperCase().includes(intent));
    }
}
