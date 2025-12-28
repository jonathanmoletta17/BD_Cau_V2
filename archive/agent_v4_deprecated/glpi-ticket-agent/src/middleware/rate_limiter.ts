import { Redis } from 'ioredis';
import { Request, Response, NextFunction } from 'express';

/**
 * Rate Limiter - Sprint 3.3
 * Proteção anti-abuso usando sliding window
 */

export interface RateLimitConfig {
    windowMs: number;    // Janela de tempo (ms)
    maxRequests: number; // Máximo de requisições na janela
    keyPrefix?: string;  // Prefixo para chaves Redis
}

export class RateLimiter {
    private readonly DEFAULT_PREFIX = 'ratelimit';

    constructor(
        private redis: Redis,
        private config: RateLimitConfig
    ) { }

    /**
     * Middleware Express para rate limiting
     */
    middleware() {
        return async (req: Request, res: Response, next: NextFunction) => {
            const userId = this.getUserId(req);
            const isLimited = await this.checkLimit(userId);

            if (isLimited) {
                const retryAfter = Math.ceil(this.config.windowMs / 1000);

                console.warn(
                    `[RateLimiter] ⚠️ User ${userId} exceeded rate limit ` +
                    `(${this.config.maxRequests} req/${this.config.windowMs}ms)`
                );

                return res.status(429).json({
                    error: 'Too many requests',
                    message: `Rate limit exceeded. Try again in ${retryAfter} seconds.`,
                    retryAfter
                });
            }

            // Permitir requisição
            await this.recordRequest(userId);
            next();
        };
    }

    /**
     * Verificar se usuário excedeu limite
     */
    async checkLimit(userId: string): Promise<boolean> {
        const key = this.getKey(userId);
        const now = Date.now();
        const windowStart = now - this.config.windowMs;

        // Remover requisições antigas
        await this.redis.zremrangebyscore(key, 0, windowStart);

        // Contar requisições na janela
        const count = await this.redis.zcard(key);

        return count >= this.config.maxRequests;
    }

    /**
     * Registrar requisição atual
     */
    async recordRequest(userId: string): Promise<void> {
        const key = this.getKey(userId);
        const now = Date.now();
        const member = `${now}-${Math.random()}`;

        // Adicionar requisição ao sorted set
        await this.redis.zadd(key, now, member);

        // Definir TTL
        const ttlSeconds = Math.ceil(this.config.windowMs / 1000) + 10;
        await this.redis.expire(key, ttlSeconds);
    }

    /**
     * Obter contador atual para usuário
     */
    async getRequestCount(userId: string): Promise<number> {
        const key = this.getKey(userId);
        const now = Date.now();
        const windowStart = now - this.config.windowMs;

        await this.redis.zremrangebyscore(key, 0, windowStart);
        return await this.redis.zcard(key);
    }

    /**
     * Resetar limite para usuário (admin)
     */
    async resetLimit(userId: string): Promise<void> {
        const key = this.getKey(userId);
        await this.redis.del(key);
        console.log(`[RateLimiter] 🔄 Reset limit for user ${userId}`);
    }

    /**
     * Obter ID do usuário a partir da request
     */
    private getUserId(req: Request): string {
        return (
            (req.headers['x-user-id'] as string) ||
            req.ip ||
            'unknown'
        );
    }

    /**
     * Gerar chave Redis
     */
    private getKey(userId: string): string {
        const prefix = this.config.keyPrefix || this.DEFAULT_PREFIX;
        return `${prefix}:${userId}`;
    }
}

/**
 * Factory para configurações pré-definidas
 */
export const RateLimitPresets = {
    /** 30 requisições por minuto */
    MODERATE: {
        windowMs: 60 * 1000,
        maxRequests: 30
    },

    /** 10 requisições por minuto */
    STRICT: {
        windowMs: 60 * 1000,
        maxRequests: 10
    },

    /** 100 requisições por minuto */
    LENIENT: {
        windowMs: 60 * 1000,
        maxRequests: 100
    },

    /** 5 requisições por 10 segundos */
    BURST_PROTECTION: {
        windowMs: 10 * 1000,
        maxRequests: 5
    }
};
