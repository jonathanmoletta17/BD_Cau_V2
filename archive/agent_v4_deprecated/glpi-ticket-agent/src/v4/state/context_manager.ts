import { LLMService } from '../../services/llm_service';
import { ConversationState } from './conversation_state';

/**
 * Context Manager - Gerencia histórico e detecta mudanças de contexto
 */
export class ContextManager {
    constructor(private llm: LLMService) { }

    /**
     * Resumir histórico se ficar muito grande (> 10 mensagens)
     */
    async summarizeIfNeeded(state: ConversationState): Promise<ConversationState> {
        if (state.history.length > 10) {
            const oldMessages = state.history.slice(0, -5); // Últimas 5 ficam intactas
            const summary = await this.generateSummary(oldMessages);

            console.log('[ContextManager] Summarizing old messages...');

            // Substituir mensagens antigas por resumo
            state.history = [
                {
                    role: 'agent',
                    message: `[Resumo da conversa anterior]: ${summary}`,
                    timestamp: new Date().toISOString()
                },
                ...state.history.slice(-5)
            ];
        }

        return state;
    }

    /**
     * Gerar resumo de mensagens antigas
     */
    private async generateSummary(messages: Array<{ role: string, message: string }>): Promise<string> {
        if (messages.length === 0) return '';

        const text = messages
            .map(m => `${m.role === 'user' ? 'Usuário' : 'Assistente'}: ${m.message}`)
            .join('\n');

        const prompt = `Resuma essa conversa em 2-3 frases curtas, mantendo informações importantes:\n\n${text}`;

        try {
            const summary = await this.llm.complete(prompt, 'Você é um assistente que resume conversas de forma concisa.');
            return summary || 'Conversa sobre suporte técnico';
        } catch (error) {
            console.error('[ContextManager] Failed to generate summary:', error);
            return 'Conversa anterior sobre suporte técnico';
        }
    }

    /**
     * Detectar mudança de tópico (usuário muda de assunto)
     */
    detectTopicChange(state: ConversationState, newMessage: string): boolean {
        if (state.history.length < 2) {
            return false; // Não há histórico suficiente
        }

        // Pegar últimas 2 mensagens do usuário
        const userMessages = state.history
            .filter((m: { role: string, message: string }) => m.role === 'user')
            .slice(-2);

        if (userMessages.length < 2) {
            return false;
        }

        const previousMessage = userMessages[0].message;
        const similarity = this.calculateSimilarity(previousMessage, newMessage);

        // Se similaridade < 30%, consideramos mudança de tópico
        const hasTopicChange = similarity < 0.3;

        if (hasTopicChange) {
            console.log(`[ContextManager] Topic change detected (similarity: ${(similarity * 100).toFixed(1)}%)`);
        }

        return hasTopicChange;
    }

    /**
     * Calcular similaridade entre dois textos (Jaccard similarity)
     */
    private calculateSimilarity(text1: string, text2: string): number {
        // Normalizar e criar sets de palavras
        const words1 = new Set(
            text1.toLowerCase()
                .replace(/[^\w\s]/g, '') // Remove pontuação
                .split(/\s+/)
                .filter(w => w.length > 2) // Ignora palavras muito curtas
        );

        const words2 = new Set(
            text2.toLowerCase()
                .replace(/[^\w\s]/g, '')
                .split(/\s+/)
                .filter(w => w.length > 2)
        );

        // Calcular interseção e união
        const intersection = new Set([...words1].filter(w => words2.has(w)));
        const union = new Set([...words1, ...words2]);

        if (union.size === 0) return 0;

        return intersection.size / union.size;
    }

    /**
     * Extrair últimas N mensagens do histórico
     */
    getRecentHistory(state: ConversationState, count: number = 5): string[] {
        return state.history
            .slice(-count)
            .map((m: { message: string }) => m.message);
    }

    /**
     * Formatar histórico para prompt do LLM
     */
    formatHistoryForPrompt(state: ConversationState, maxMessages: number = 10): string {
        const recentMessages = state.history.slice(-maxMessages);

        return recentMessages
            .map((m: { role: string, message: string }) => `${m.role === 'user' ? 'Usuário' : 'Assistente'}: ${m.message}`)
            .join('\n');
    }
}
