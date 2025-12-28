import { Redis } from 'ioredis';

/**
 * Audit Logger - Sprint 3.2
 * Rastreamento de ações críticas para compliance e governança
 */

export type AuditAction =
    | 'CHAT_MESSAGE'
    | 'TICKET_CREATE'
    | 'USER_CREATE'
    | 'ERROR'
    | 'RATE_LIMIT_EXCEEDED'
    | 'SAFETY_BLOCKED';

export type AuditResult = 'SUCCESS' | 'FAILURE' | 'BLOCKED';

export interface AuditEvent {
    eventId: string;
    timestamp: string;
    userId: string;
    action: AuditAction;
    intent?: string;
    payload: any;
    result: AuditResult;
    reason?: string;
    metadata?: Record<string, any>;
}

export class AuditLogger {
    private readonly TTL_DAYS = 30;
    private readonly MAX_USER_EVENTS = 100;

    constructor(private redis: Redis) { }

    /**
     * Registrar evento de auditoria
     */
    async log(event: Omit<AuditEvent, 'eventId' | 'timestamp'>): Promise<string> {
        const auditEvent: AuditEvent = {
            eventId: this.generateEventId(),
            timestamp: new Date().toISOString(),
            ...event
        };

        try {
            // Salvar evento completo no Redis
            const key = `audit:${auditEvent.eventId}`;
            const ttlSeconds = this.TTL_DAYS * 24 * 3600;

            await this.redis.set(
                key,
                JSON.stringify(auditEvent),
                'EX',
                ttlSeconds
            );

            // Adicionar à lista de eventos do usuário (últimos N eventos)
            const userKey = `audit:user:${event.userId}`;
            await this.redis.lpush(userKey, auditEvent.eventId);
            await this.redis.ltrim(userKey, 0, this.MAX_USER_EVENTS - 1);
            await this.redis.expire(userKey, ttlSeconds);

            // Adicionar à lista global de eventos recentes
            const globalKey = 'audit:global:recent';
            await this.redis.lpush(globalKey, auditEvent.eventId);
            await this.redis.ltrim(globalKey, 0, 999); // Últimos 1000
            await this.redis.expire(globalKey, ttlSeconds);

            // Log no console para debug
            console.log(
                `[AuditLogger] 📝 ${event.action} by ${event.userId}: ${event.result}`,
                event.reason ? `(${event.reason})` : ''
            );

            return auditEvent.eventId;
        } catch (error: any) {
            console.error('[AuditLogger] ❌ Failed to log event:', error.message);
            throw error;
        }
    }

    /**
     * Buscar trilha de auditoria de um usuário
     */
    async getUserAuditTrail(
        userId: string,
        limit: number = 20
    ): Promise<AuditEvent[]> {
        const userKey = `audit:user:${userId}`;
        const eventIds = await this.redis.lrange(userKey, 0, limit - 1);

        const events: AuditEvent[] = [];
        for (const eventId of eventIds) {
            const key = `audit:${eventId}`;
            const raw = await this.redis.get(key);

            if (raw) {
                try {
                    events.push(JSON.parse(raw));
                } catch (error) {
                    console.error(`[AuditLogger] Failed to parse event ${eventId}`);
                }
            }
        }

        return events;
    }

    /**
     * Buscar eventos recentes (últimos N)
     */
    async getRecentEvents(limit: number = 50): Promise<AuditEvent[]> {
        const globalKey = 'audit:global:recent';
        const eventIds = await this.redis.lrange(globalKey, 0, limit - 1);

        const events: AuditEvent[] = [];
        for (const eventId of eventIds) {
            const key = `audit:${eventId}`;
            const raw = await this.redis.get(key);

            if (raw) {
                try {
                    events.push(JSON.parse(raw));
                } catch (error) {
                    console.error(`[AuditLogger] Failed to parse event ${eventId}`);
                }
            }
        }

        return events;
    }

    /**
     * Buscar eventos por ação
     */
    async getEventsByAction(
        action: AuditAction,
        limit: number = 50
    ): Promise<AuditEvent[]> {
        // Buscar dos recentes e filtrar
        const recent = await this.getRecentEvents(200);
        return recent
            .filter(e => e.action === action)
            .slice(0, limit);
    }

    /**
     * Estatísticas de auditoria
     */
    async getStats(userId?: string): Promise<{
        totalEvents: number;
        byAction: Record<AuditAction, number>;
        byResult: Record<AuditResult, number>;
    }> {
        const events = userId
            ? await this.getUserAuditTrail(userId, 1000)
            : await this.getRecentEvents(1000);

        const stats = {
            totalEvents: events.length,
            byAction: {} as Record<AuditAction, number>,
            byResult: {} as Record<AuditResult, number>
        };

        for (const event of events) {
            // Contar por ação
            stats.byAction[event.action] = (stats.byAction[event.action] || 0) + 1;

            // Contar por resultado
            stats.byResult[event.result] = (stats.byResult[event.result] || 0) + 1;
        }

        return stats;
    }

    /**
     * Gerar ID único para evento
     */
    private generateEventId(): string {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 11);
        return `audit-${timestamp}-${random}`;
    }
}
