import { Redis } from 'ioredis';

/**
 * TelemetryService - Captura e armazena decisões dos agentes para observabilidade
 */

export interface TelemetryEvent {
    timestamp: string;
    conversationId: string;
    agent: 'Router' | 'FormAgentV4' | 'IncidentAgent' | 'System';
    phase: 'classification' | 'processing' | 'generation' | 'completion';
    input: string;
    decision?: string;
    confidence?: number;
    reasoning: {
        keywords_found?: string[];
        entity_detected?: {
            keyword: string;
            mapped_to: { id: number; name: string };
        };
        rag_context?: {
            entities_found: number;
            categories_found: number;
            rules_applied: string[];
            relevance_score: number;
        };
        diagnostic_step?: number;
        extracted_fields?: Record<string, any>;
        llm_raw_response?: string;
        fallback_used?: boolean;
        error?: string;
        alternative_intents?: Record<string, number>;
    };
    timing: {
        started_at: string;
        completed_at: string;
        duration_ms: number;
    };
    metadata?: Record<string, any>;
}

export interface ConversationTelemetry {
    conversationId: string;
    userId: string;
    events: TelemetryEvent[];
    summary: {
        total_events: number;
        total_duration_ms: number;
        agents_used: string[];
        final_intent?: string;
    };
}

export class TelemetryService {
    private readonly TTL_SECONDS = 86400; // 24 horas

    constructor(private redis: Redis) { }

    /**
     * Registra um evento de telemetria
     */
    async track(event: TelemetryEvent): Promise<void> {
        const key = `telemetry:${event.conversationId}`;

        // Adicionar à lista de eventos
        await this.redis.rpush(key, JSON.stringify(event));
        await this.redis.expire(key, this.TTL_SECONDS);

        // Log estruturado no console
        console.log('[Telemetry]', JSON.stringify({
            agent: event.agent,
            phase: event.phase,
            decision: event.decision,
            confidence: event.confidence,
            duration_ms: event.timing.duration_ms
        }));
    }

    /**
     * Cria um evento de telemetria com timer
     */
    createEvent(
        conversationId: string,
        agent: TelemetryEvent['agent'],
        phase: TelemetryEvent['phase'] = 'processing'
    ): {
        complete: (data: Partial<TelemetryEvent>) => Promise<void>;
        startTime: number;
    } {
        const startTime = Date.now();
        const started_at = new Date().toISOString();

        return {
            startTime,
            complete: async (data: Partial<TelemetryEvent>) => {
                const completed_at = new Date().toISOString();
                const duration_ms = Date.now() - startTime;

                await this.track({
                    timestamp: started_at,
                    conversationId,
                    agent,
                    phase,
                    input: data.input || '',
                    decision: data.decision,
                    confidence: data.confidence,
                    reasoning: data.reasoning || {},
                    timing: {
                        started_at,
                        completed_at,
                        duration_ms
                    },
                    metadata: data.metadata
                });
            }
        };
    }

    /**
     * Obtém todos os eventos de uma conversa
     */
    async getConversationTelemetry(conversationId: string): Promise<ConversationTelemetry | null> {
        const key = `telemetry:${conversationId}`;
        const rawEvents = await this.redis.lrange(key, 0, -1);

        if (rawEvents.length === 0) {
            return null;
        }

        const events: TelemetryEvent[] = rawEvents.map(e => JSON.parse(e));

        // Calcular resumo
        const agents_used = [...new Set(events.map(e => e.agent))];
        const total_duration_ms = events.reduce((sum, e) => sum + e.timing.duration_ms, 0);
        const final_intent = events.find(e => e.agent === 'Router')?.decision;

        return {
            conversationId,
            userId: events[0]?.metadata?.userId || 'unknown',
            events,
            summary: {
                total_events: events.length,
                total_duration_ms,
                agents_used,
                final_intent
            }
        };
    }

    /**
     * Obtém estatísticas gerais
     */
    async getStats(): Promise<{
        total_conversations: number;
        avg_duration_ms: number;
        agents_usage: Record<string, number>;
    }> {
        const keys = await this.redis.keys('telemetry:*');

        let totalDuration = 0;
        const agentsUsage: Record<string, number> = {};

        for (const key of keys.slice(0, 100)) { // Limitar a 100 conversas mais recentes
            const events = await this.redis.lrange(key, 0, -1);

            events.forEach(rawEvent => {
                const event: TelemetryEvent = JSON.parse(rawEvent);
                totalDuration += event.timing.duration_ms;
                agentsUsage[event.agent] = (agentsUsage[event.agent] || 0) + 1;
            });
        }

        return {
            total_conversations: keys.length,
            avg_duration_ms: keys.length > 0 ? totalDuration / keys.length : 0,
            agents_usage: agentsUsage
        };
    }

    /**
     * Formata telemetria para exibição
     */
    formatTimeline(telemetry: ConversationTelemetry): string {
        const lines: string[] = [
            `┌─ Conversa: ${telemetry.conversationId} ─────────────────────┐`,
            `│ Total: ${telemetry.summary.total_duration_ms}ms | Eventos: ${telemetry.summary.total_events} │`,
            `├──────────────────────────────────────────────────────────┤`
        ];

        telemetry.events.forEach((event, idx) => {
            const time = new Date(event.timestamp).toLocaleTimeString('pt-BR');
            lines.push(`│ ${time} [${event.agent}] ${event.phase}`);

            if (event.decision) {
                lines.push(`│   → ${event.decision} ${event.confidence ? `(${Math.round(event.confidence * 100)}%)` : ''}`);
            }

            if (event.reasoning.keywords_found?.length) {
                lines.push(`│   📌 Keywords: ${event.reasoning.keywords_found.join(', ')}`);
            }

            if (event.reasoning.entity_detected) {
                const e = event.reasoning.entity_detected;
                lines.push(`│   🎯 Entidade: ${e.keyword} → ${e.mapped_to.name} (ID: ${e.mapped_to.id})`);
            }

            if (event.reasoning.rag_context) {
                const rag = event.reasoning.rag_context;
                lines.push(`│   📚 RAG: ${rag.entities_found} entidades, ${rag.categories_found} categorias (${Math.round(rag.relevance_score * 100)}%)`);
            }

            lines.push(`│   ⏱️  ${event.timing.duration_ms}ms`);

            if (idx < telemetry.events.length - 1) {
                lines.push(`│`);
            }
        });

        lines.push(`└──────────────────────────────────────────────────────────┘`);

        return lines.join('\n');
    }
}
