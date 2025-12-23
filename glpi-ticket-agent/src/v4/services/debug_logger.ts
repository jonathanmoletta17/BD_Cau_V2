import { Redis } from 'ioredis';

/**
 * DebugLogger - Logging detalhado de decisões do sistema
 * Armazena no Redis para análise posterior
 */

export interface DebugLogEntry {
    timestamp: string;
    conversationId: string;
    userId: string;

    // Input
    userMessage: string;

    // Router Decision
    routerIntent: string;
    routerConfidence: number;
    routerMethod: 'llm' | 'fallback';
    routerRawResponse?: string;

    // Field Extraction (se aplicável)
    extractedFields?: Record<string, any>;
    fieldValidationErrors?: string[];
    fieldValidationWarnings?: string[];

    // Entity Detection
    entityDetected?: {
        keyword: string;
        matched: string;
        method: 'exact' | 'fuzzy' | 'substring';
        confidence: number;
    };

    // Final Decision
    agentUsed: string;
    responseType: string;
    responseTime: number;

    // Errors
    errors?: string[];
}

export class DebugLogger {
    private readonly MAX_LOGS = 1000;
    private readonly TTL_SECONDS = 86400; // 24h

    constructor(private redis: Redis) { }

    /**
     * Loga uma decisão completa do sistema
     */
    async logDecision(entry: DebugLogEntry): Promise<void> {
        const key = `debug:log:${entry.conversationId}`;

        // Adicionar à lista
        await this.redis.lpush(key, JSON.stringify(entry));

        // Manter apenas últimos MAX_LOGS
        await this.redis.ltrim(key, 0, this.MAX_LOGS - 1);

        // Set TTL
        await this.redis.expire(key, this.TTL_SECONDS);

        // Log estruturado no console
        console.log('[DEBUG]', {
            conversationId: entry.conversationId,
            intent: entry.routerIntent,
            method: entry.routerMethod,
            agent: entry.agentUsed,
            responseTime: `${entry.responseTime}ms`,
            errors: entry.errors?.length || 0
        });
    }

    /**
     * Obtém logs de uma conversa
     */
    async getConversationLogs(conversationId: string): Promise<DebugLogEntry[]> {
        const key = `debug:log:${conversationId}`;
        const logs = await this.redis.lrange(key, 0, -1);
        return logs.map(log => JSON.parse(log));
    }

    /**
     * Obtém estatísticas gerais
     */
    async getStats(): Promise<{
        totalLogs: number;
        intentDistribution: Record<string, number>;
        avgResponseTime: number;
        errorRate: number;
        fallbackRate: number;
    }> {
        // Buscar todas as conversas (últimas 100)
        const keys = await this.redis.keys('debug:log:*');
        const recentKeys = keys.slice(0, 100);

        let totalLogs = 0;
        const intentCounts: Record<string, number> = {};
        let totalResponseTime = 0;
        let errorCount = 0;
        let fallbackCount = 0;

        for (const key of recentKeys) {
            const logs = await this.redis.lrange(key, 0, -1);

            for (const logStr of logs) {
                const log: DebugLogEntry = JSON.parse(logStr);
                totalLogs++;

                // Intent distribution
                intentCounts[log.routerIntent] = (intentCounts[log.routerIntent] || 0) + 1;

                // Response time
                totalResponseTime += log.responseTime;

                // Errors
                if (log.errors && log.errors.length > 0) {
                    errorCount++;
                }

                // Fallback usage
                if (log.routerMethod === 'fallback') {
                    fallbackCount++;
                }
            }
        }

        return {
            totalLogs,
            intentDistribution: intentCounts,
            avgResponseTime: totalLogs > 0 ? totalResponseTime / totalLogs : 0,
            errorRate: totalLogs > 0 ? (errorCount / totalLogs) * 100 : 0,
            fallbackRate: totalLogs > 0 ? (fallbackCount / totalLogs) * 100 : 0
        };
    }

    /**
     * Formata logs para exibição
     */
    formatLogs(logs: DebugLogEntry[]): string {
        const lines: string[] = ['╔════════════════════════════════════════════╗'];
        lines.push('║         DEBUG LOG TIMELINE                  ║');
        lines.push('╚════════════════════════════════════════════╝');
        lines.push('');

        logs.reverse().forEach((log, idx) => {
            const time = new Date(log.timestamp).toLocaleTimeString('pt-BR');
            lines.push(`[${idx + 1}] ${time}`);
            lines.push(`  User: ${log.userMessage}`);
            lines.push(`  Router: ${log.routerIntent} (${log.routerMethod}, ${log.routerConfidence}%)`);

            if (log.entityDetected) {
                lines.push(`  Entity: "${log.entityDetected.keyword}" → ${log.entityDetected.matched} (${log.entityDetected.method})`);
            }

            if (log.extractedFields) {
                lines.push(`  Fields: ${Object.keys(log.extractedFields).join(', ')}`);
            }

            if (log.fieldValidationErrors && log.fieldValidationErrors.length > 0) {
                lines.push(`  ⚠️  Validation errors: ${log.fieldValidationErrors.length}`);
            }

            lines.push(`  Agent: ${log.agentUsed} (${log.responseTime}ms)`);

            if (log.errors && log.errors.length > 0) {
                lines.push(`  ❌ Errors: ${log.errors.join(', ')}`);
            }

            lines.push('');
        });

        return lines.join('\n');
    }

    /**
     * Endpoint para exportar logs em formato CSV
     */
    async exportCSV(conversationIds: string[]): Promise<string> {
        const header = [
            'timestamp',
            'conversationId',
            'userId',
            'userMessage',
            'routerIntent',
            'routerConfidence',
            'routerMethod',
            'agentUsed',
            'responseType',
            'responseTime',
            'errors'
        ].join(',');

        const rows: string[] = [header];

        for (const convId of conversationIds) {
            const logs = await this.getConversationLogs(convId);

            for (const log of logs) {
                const row = [
                    log.timestamp,
                    log.conversationId,
                    log.userId,
                    `"${log.userMessage.replace(/"/g, '""')}"`,
                    log.routerIntent,
                    log.routerConfidence,
                    log.routerMethod,
                    log.agentUsed,
                    log.responseType,
                    log.responseTime,
                    log.errors ? `"${log.errors.join('; ')}"` : ''
                ].join(',');

                rows.push(row);
            }
        }

        return rows.join('\n');
    }
}
