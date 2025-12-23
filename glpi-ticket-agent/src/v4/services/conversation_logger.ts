import { Redis } from 'ioredis';
import * as fs from 'fs';

/**
 * ConversationLogger - Sistema de logging de conversas para fine-tuning
 * 
 * Coleta conversas reais para:
 * - Fine-tuning com NVIDIA TensorRT-LLM
 * - LoRA training
 * - Análise de comportamento
 */

export interface ConversationTurn {
    turnId: number;
    timestamp: string;
    input: string;
    router_intent: string;
    router_confidence: number;
    router_raw_response?: string;
    agent_type: 'FormAgentV4' | 'IncidentAgent' | 'Router';
    agent_response: string;
    response_type: 'TEXT' | 'FORM' | 'WIDGET';
    entities_detected?: Array<{
        keyword: string;
        mapped_to: { id: number; name: string };
    }>;
    form_generated?: any;
    rag_context_used?: {
        entities: number;
        categories: number;
        relevance_score: number;
    };
    user_feedback?: 'helpful' | 'not_helpful' | null;
    feedback_comment?: string;
    timing: {
        router_ms: number;
        agent_ms: number;
        total_ms: number;
    };
}

export interface ConversationLog {
    conversationId: string;
    userId: string;
    startedAt: string;
    lastActivityAt: string;
    turns: ConversationTurn[];
    metadata: {
        totalTurns: number;
        avgResponseTime: number;
        successfulResolution: boolean;
        finalIntent?: string;
    };
}

export class ConversationLogger {
    private readonly TTL_SECONDS = 86400 * 7; // 7 dias no Redis

    constructor(private redis: Redis) { }

    /**
     * Inicia uma nova conversa
     */
    async startConversation(conversationId: string, userId: string): Promise<void> {
        const log: ConversationLog = {
            conversationId,
            userId,
            startedAt: new Date().toISOString(),
            lastActivityAt: new Date().toISOString(),
            turns: [],
            metadata: {
                totalTurns: 0,
                avgResponseTime: 0,
                successfulResolution: false
            }
        };

        await this.saveConversation(conversationId, log);
    }

    /**
     * Adiciona um turno à conversa
     */
    async addTurn(conversationId: string, turn: Omit<ConversationTurn, 'turnId' | 'timestamp'>): Promise<void> {
        const log = await this.getConversation(conversationId);

        if (!log) {
            console.error(`[ConversationLogger] Conversa não encontrada: ${conversationId}`);
            return;
        }

        const completeTurn: ConversationTurn = {
            ...turn,
            turnId: log.turns.length + 1,
            timestamp: new Date().toISOString(),
            user_feedback: null
        };

        log.turns.push(completeTurn);
        log.lastActivityAt = new Date().toISOString();
        log.metadata.totalTurns = log.turns.length;
        log.metadata.avgResponseTime = log.turns.reduce((sum, t) => sum + t.timing.total_ms, 0) / log.turns.length;

        await this.saveConversation(conversationId, log);

        // Log estruturado para análise
        console.log('[ConversationLogger] Turn added:', JSON.stringify({
            conversationId,
            turnId: completeTurn.turnId,
            intent: completeTurn.router_intent,
            responseTime: completeTurn.timing.total_ms
        }));
    }

    /**
     * Adiciona feedback do usuário
     */
    async addFeedback(
        conversationId: string,
        turnId: number,
        feedback: 'helpful' | 'not_helpful',
        comment?: string
    ): Promise<void> {
        const log = await this.getConversation(conversationId);

        if (!log) return;

        const turn = log.turns.find(t => t.turnId === turnId);
        if (turn) {
            turn.user_feedback = feedback;
            turn.feedback_comment = comment;

            // Marcar conversa como resolvida com sucesso se feedback positivo
            if (feedback === 'helpful') {
                log.metadata.successfulResolution = true;
            }

            await this.saveConversation(conversationId, log);
        }
    }

    /**
     * Obtém uma conversa do Redis
     */
    async getConversation(conversationId: string): Promise<ConversationLog | null> {
        const key = `conversation:log:${conversationId}`;
        const data = await this.redis.get(key);

        return data ? JSON.parse(data) : null;
    }

    /**
     * Salva conversa no Redis
     */
    private async saveConversation(conversationId: string, log: ConversationLog): Promise<void> {
        const key = `conversation:log:${conversationId}`;
        await this.redis.set(key, JSON.stringify(log), 'EX', this.TTL_SECONDS);
    }

    /**
     * Exporta conversas para file (backup/análise)
     */
    async exportToFile(conversationId: string, filepath: string): Promise<void> {
        const log = await this.getConversation(conversationId);

        if (log) {
            fs.writeFileSync(filepath, JSON.stringify(log, null, 2));
            console.log(`[ConversationLogger] Exportado: ${filepath}`);
        }
    }

    /**
     * Obtém todas as conversas (para export em batch)
     */
    async getAllConversationIds(): Promise<string[]> {
        const keys = await this.redis.keys('conversation:log:*');
        return keys.map(key => key.replace('conversation:log:', ''));
    }

    /**
     * Obtém estatísticas gerais
     */
    async getStats(): Promise<{
        total_conversations: number;
        total_turns: number;
        avg_turns_per_conversation: number;
        feedback_rate: number;
        positive_feedback_rate: number;
        avg_response_time: number;
    }> {
        const ids = await this.getAllConversationIds();
        let totalTurns = 0;
        let feedbackCount = 0;
        let positiveFeedbackCount = 0;
        let totalResponseTime = 0;

        for (const id of ids) {
            const log = await this.getConversation(id);
            if (!log) continue;

            totalTurns += log.turns.length;
            totalResponseTime += log.metadata.avgResponseTime;

            log.turns.forEach(turn => {
                if (turn.user_feedback) {
                    feedbackCount++;
                    if (turn.user_feedback === 'helpful') {
                        positiveFeedbackCount++;
                    }
                }
            });
        }

        return {
            total_conversations: ids.length,
            total_turns: totalTurns,
            avg_turns_per_conversation: ids.length > 0 ? totalTurns / ids.length : 0,
            feedback_rate: totalTurns > 0 ? feedbackCount / totalTurns : 0,
            positive_feedback_rate: feedbackCount > 0 ? positiveFeedbackCount / feedbackCount : 0,
            avg_response_time: ids.length > 0 ? totalResponseTime / ids.length : 0
        };
    }
}
