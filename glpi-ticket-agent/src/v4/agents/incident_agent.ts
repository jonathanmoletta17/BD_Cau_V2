
import { LLMService } from '../../services/llm_service';
import { RAGService } from '../services/rag_service';
import { TelemetryService } from '../services/telemetry_service';
import { AgentResponse } from '../types';

/**
 * IncidentAgent - Diagnóstico conversacional com RAG + Telemetria
 */
export class IncidentAgent {
    private ragService: RAGService;

    constructor(
        private llm: LLMService,
        private telemetry?: TelemetryService
    ) {
        this.ragService = new RAGService();
    }

    async process(message: string, history: string[], conversationId?: string): Promise<AgentResponse> {
        // Iniciar telemetria
        const telemetryEvent = conversationId && this.telemetry
            ? this.telemetry.createEvent(conversationId, 'IncidentAgent', 'processing')
            : null;

        // Buscar contexto relevante (categorias e procedimentos)
        const ragResult = this.ragService.search(message);
        const ragContext = ragResult.categories.length > 0
            ? `\n${this.ragService.formatContext(ragResult)}\n`
            : '';

        const systemPrompt = `
Você é um agente de diagnóstico técnico.
O usuário relatou um problema. Faça perguntas para entender melhor.
${ragContext}
HISTÓRICO da conversa:
${history.slice(-5).join('\n')}

Faça UMA pergunta de cada vez para diagnosticar o problema.
`.trim();

        try {
            const response = await this.llm.complete(message, systemPrompt);

            // Completar telemetria
            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: 'Diagnostic question generated',
                    reasoning: {
                        rag_context: {
                            entities_found: ragResult.entities.length,
                            categories_found: ragResult.categories.length,
                            rules_applied: ragResult.rules.map(r => r.topic),
                            relevance_score: ragResult.relevanceScore
                        },
                        diagnostic_step: history.length + 1
                    }
                });
            }

            return {
                type: 'TEXT',
                message: response,
                metadata: { intent: 'INCIDENT' }
            };

        } catch (error: any) {
            console.error('[IncidentAgent] Erro:', error);

            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: 'Error',
                    reasoning: {}
                });
            }

            return {
                type: 'TEXT',
                message: 'Desculpe, houve um erro. Pode descrever o problema novamente?',
                metadata: { intent: 'INCIDENT' }
            };
        }
    }
}
