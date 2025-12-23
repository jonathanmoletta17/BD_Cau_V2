
import Redis from 'ioredis';
import { AgentContext } from '../core/types';

export interface SessionRepository {
    getSession(sessionId: string): Promise<AgentContext | null>;
    saveSession(context: AgentContext): Promise<void>;
    deleteSession(sessionId: string): Promise<void>;
}

export class RedisSessionRepository implements SessionRepository {
    private client: Redis;
    private ttl: number = 3600; // 1 Hour Session TTL

    constructor() {
        // Connect to Redis Container (hostname 'glpi-redis' if in docker network, or 'localhost' if running native against mapped port)
        const host = process.env.REDIS_HOST || 'localhost';
        const port = Number(process.env.REDIS_PORT) || 6379;

        console.log(`[Redis] Connecting to ${host}:${port}...`);

        this.client = new Redis({
            host: host,
            port: port,
            password: '', // No password for dev
            retryStrategy: (times) => Math.min(times * 50, 2000)
        });

        this.client.on('error', (err) => console.error('[Redis] Error:', err));
        this.client.on('connect', () => console.log('[Redis] Connected'));
    }

    async getSession(sessionId: string): Promise<AgentContext | null> {
        const data = await this.client.get(`session:${sessionId}`);
        if (!data) return null;
        return JSON.parse(data);
    }

    async saveSession(context: AgentContext): Promise<void> {
        await this.client.setex(
            `session:${context.sessionId}`,
            this.ttl,
            JSON.stringify(context)
        );
    }

    async deleteSession(sessionId: string): Promise<void> {
        await this.client.del(`session:${sessionId}`);
    }
}
