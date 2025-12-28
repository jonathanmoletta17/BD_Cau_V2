
import { LLMService } from '../../services/llm_service';
import { RAGService } from '../services/rag_service';
import { TelemetryService } from '../services/telemetry_service';
import { ConversationState, ConversationStateManager } from '../state/conversation_state';
import { AgentResponse } from '../types';

/**
 * IncidentAgent V2 - Diagnóstico conversacional estruturado com perguntas do RAG
 * Usa customData para armazenar estado do diagnóstico
 */
export class IncidentAgent {
    private ragService: RAGService;

    constructor(
        private llm: LLMService,
        private stateManager: ConversationStateManager,
        private telemetry?: TelemetryService
    ) {
        this.ragService = new RAGService();
    }

    /**
     * Processar mensagem inicial do incidente
     */
    async process(message: string, history: string[], conversationId: string): Promise<AgentResponse> {
        console.log('[IncidentAgent] 🔍 process() called:', { message, conversationId });

        const telemetryEvent = conversationId && this.telemetry
            ? this.telemetry.createEvent(conversationId, 'IncidentAgent', 'processing')
            : null;

        // Carregar estado
        const state = await this.stateManager.getOrCreate(conversationId, 'unknown');
        console.log('[IncidentAgent] 📊 State loaded:', { hasCustomData: !!state.customData, historyLength: state.history.length });

        // Inicializar customData para INCIDENT se não existir
        if (!state.customData) {
            state.customData = {
                intent: 'INCIDENT',
                initialProblem: message,
                askedQuestions: [],
                answers: {}
            };
        }

        // Buscar contexto relevante
        const ragResult = this.ragService.search(message);
        const category = ragResult.categories[0];

        console.log('[IncidentAgent] 🔎 RAG search:', {
            categoriesFound: ragResult.categories.length,
            categoryName: category?.name || 'NONE',
            diagnosticSteps: category?.diagnosticSteps.length || 0
        });

        if (!category) {
            console.log('[IncidentAgent] ⚠️ No category found, using fallback LLM');
            // Sem categoria encontrada → usar LLM genérico
            return this.fallbackToGenericQuestion(message, history, state, telemetryEvent);
        }

        // Usar perguntas estruturadas do diagnosticSteps
        const diagnosticSteps = category.diagnosticSteps;
        const askedQuestions = state.customData.askedQuestions || [];

        console.log('[IncidentAgent] 📝 Diagnostic steps:', { total: diagnosticSteps.length, asked: askedQuestions.length });

        // Encontrar próxima pergunta não feita
        const nextQuestion = diagnosticSteps.find((q: string) => !askedQuestions.includes(q));

        console.log('[IncidentAgent] ❓ Next question:', { found: !!nextQuestion, question: nextQuestion?.substring(0, 50) });

        if (nextQuestion) {
            // Adicionar pergunta ao histórico
            this.stateManager.addMessage(state, 'agent', nextQuestion);

            // Marcar como feita
            state.customData.askedQuestions.push(nextQuestion);
            state.customData.category = category.name;

            await this.stateManager.save(state);

            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: `Structured question ${askedQuestions.length + 1}/${diagnosticSteps.length}`,
                    reasoning: {}
                });
            }

            return {
                type: 'TEXT',
                message: nextQuestion,
                metadata: {
                    intent: 'INCIDENT'
                }
            };
        } else {
            console.log('[IncidentAgent] 📊 All questions asked, generating solution');
            // Todas perguntas feitas → gerar resumo e oferecer solução
            return this.generateSolution(state, ragResult, telemetryEvent);
        }
    }

    /**
     * Continuar diálogo de diagnóstico (resposta do usuário)
     */
    async continueDialog(conversationId: string, userAnswer: string): Promise<AgentResponse> {
        const state = await this.stateManager.getOrCreate(conversationId, 'unknown');

        if (!state.customData) {
            state.customData = { intent: 'INCIDENT', answers: {}, askedQuestions: [] };
        }

        // Armazenar resposta do usuário
        const answerIndex = (state.customData.askedQuestions?.length || 0);
        state.customData.answers[`answer_${answerIndex}`] = userAnswer;

        this.stateManager.addMessage(state, 'user', userAnswer);

        // Buscar próxima pergunta
        const ragResult = this.ragService.search(state.customData.initialProblem || 'technical problem');
        const category = ragResult.categories[0];

        if (!category) {
            return this.generateSolution(state, ragResult, null);
        }

        const diagnosticSteps = category.diagnosticSteps;
        const askedQuestions = state.customData.askedQuestions || [];
        const nextQuestion = diagnosticSteps.find((q: string) => !askedQuestions.includes(q));

        if (nextQuestion) {
            // Ainda há perguntas
            this.stateManager.addMessage(state, 'agent', nextQuestion);
            state.customData.askedQuestions.push(nextQuestion);

            await this.stateManager.save(state);

            return {
                type: 'TEXT',
                message: nextQuestion,
                metadata: {
                    intent: 'INCIDENT'
                }
            };
        } else {
            // Todas perguntas feitas → gerar solução
            return this.generateSolution(state, ragResult, null);
        }
    }

    /**
     * Gerar solução baseada nas respostas coletadas
     */
    private async generateSolution(
        state: ConversationState,
        ragResult: any,
        telemetryEvent: any
    ): Promise<AgentResponse> {
        const answers = state.customData?.answers || {};
        const answerTexts = Object.values(answers) as string[];

        // Resumir problema e respostas
        const summary = `**Resumo do problema:**\n- Problema: ${state.customData?.initialProblem || 'Não especificado'}\n- Diagnóstico: ${answerTexts.join(', ')}`;

        // Buscar solução na Knowledge Base (FAQs)
        const relatedFAQs = ragResult.faqs.slice(0, 2);

        let solutionText = '';
        if (relatedFAQs.length > 0) {
            solutionText = `\n\n**Possível solução:**\n${relatedFAQs[0].answer}`;
        } else {
            solutionText = '\n\n**Recomendação:** Encaminhar para suporte técnico especializado.';
        }

        // Mudar step para awaiting_confirmation
        state.currentStep = 'awaiting_confirmation';
        await this.stateManager.save(state);

        if (telemetryEvent) {
            await telemetryEvent.complete({
                input: 'All diagnostic questions answered',
                decision: 'Generate solution',
                reasoning: {
                    answers_collected: answerTexts.length,
                    faqs_found: relatedFAQs.length
                }
            });
        }

        return {
            type: 'TEXT',
            message: `${summary}${solutionText}\n\n**Deseja que eu crie um ticket com essas informações?** (Responda "Sim" para confirmar)`,
            metadata: {
                intent: 'INCIDENT'
            }
        };
    }

    /**
     * Fallback para pergunta genérica via LLM quando RAG não encontra categoria
     */
    private async fallbackToGenericQuestion(
        message: string,
        history: string[],
        state: ConversationState,
        telemetryEvent: any
    ): Promise<AgentResponse> {
        const systemPrompt = `
Você é um agente de diagnóstico técnico.
O usuário relatou um problema. Faça UMA pergunta específica e técnica para entender melhor.

HISTÓRICO:
${history.slice(-3).join('\n')}

Faça uma pergunta técnica direta e objetiva.
        `.trim();

        try {
            console.log('[IncidentAgent] 🤖 Calling LLM for generic question...');
            const response = await this.llm.complete(message, systemPrompt);

            console.log('[IncidentAgent] 📥 LLM response:', { length: response?.length || 0, preview: response?.substring(0, 50) });

            this.stateManager.addMessage(state, 'agent', response);
            await this.stateManager.save(state);

            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: 'Generic LLM question (no RAG category)',
                    reasoning: {}
                });
            }

            return {
                type: 'TEXT',
                message: response,
                metadata: { intent: 'INCIDENT' }
            };
        } catch (error: any) {
            console.error('[IncidentAgent] Erro:', error);

            return {
                type: 'TEXT',
                message: 'Desculpe, houve um erro. Pode descrever o problema novamente?',
                metadata: { intent: 'INCIDENT' }
            };
        }
    }
}
