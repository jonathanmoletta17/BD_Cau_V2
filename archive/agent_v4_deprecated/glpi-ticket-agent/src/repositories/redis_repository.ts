
import Redis from 'ioredis';

// V1 AgentContext removed - TOD V2 uses Redis client directly
// This class only provides Redis client access for TOD architecture

export class RedisSessionRepository {
    public client: Redis;  // Public for TOD agent access
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

    // V1 methods removed - TOD V2 uses Redis client directly via StateTracker
}
