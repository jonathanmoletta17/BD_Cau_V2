import crypto from 'crypto';
import { Redis } from 'ioredis';

/**
 * Cache Service for LLM responses
 * Caches NLU extractions and NLG responses to reduce latency
 */
export class CacheService {
    private client: Redis;
    private ttl: number = 86400; // 24 hours
    private nluHits: number = 0;
    private nluMisses: number = 0;
    private nlgHits: number = 0;
    private nlgMisses: number = 0;

    constructor(redisClient: Redis) {
        this.client = redisClient;
        console.log('[CacheService] Initialized with 24h TTL');
    }

    /**
     * Generate MD5 hash for cache key
     */
    private hash(message: string, context?: any): string {
        const content = context
            ? `${message}:${JSON.stringify(context)}`
            : message;
        return crypto.createHash('md5')
            .update(content.toLowerCase().trim())
            .digest('hex');
    }

    /**
     * Get cached NLU extraction
     */
    async getNLUCache(message: string, context?: any): Promise<any | null> {
        try {
            const key = `nlu:${this.hash(message, context)}`;
            const cached = await this.client.get(key);

            if (cached) {
                this.nluHits++;
                console.log(`[Cache] 🎯 NLU HIT: "${message.substring(0, 40)}..." (hits: ${this.nluHits})`);
                return JSON.parse(cached);
            }

            this.nluMisses++;
            console.log(`[Cache] ❌ NLU MISS: "${message.substring(0, 40)}..." (misses: ${this.nluMisses})`);
            return null;
        } catch (error) {
            console.error('[Cache] Error getting NLU cache:', error);
            return null;
        }
    }

    /**
     * Set NLU cache
     */
    async setNLUCache(message: string, result: any, context?: any): Promise<void> {
        try {
            const key = `nlu:${this.hash(message, context)}`;
            await this.client.set(key, JSON.stringify(result), 'EX', this.ttl);
            console.log(`[Cache] 💾 NLU SET: "${message.substring(0, 40)}..."`);
        } catch (error) {
            console.error('[Cache] Error setting NLU cache:', error);
        }
    }

    /**
     * Get cached NLG response
     */
    async getNLGCache(actionType: string, slot?: string, context?: any): Promise<string | null> {
        try {
            const contextKey = slot || JSON.stringify(context || {});
            const key = `nlg:${actionType}:${this.hash(contextKey)}`;
            const cached = await this.client.get(key);

            if (cached) {
                this.nlgHits++;
                console.log(`[Cache] 🎯 NLG HIT: ${actionType}/${slot || 'general'} (hits: ${this.nlgHits})`);
                return cached;
            }

            this.nlgMisses++;
            console.log(`[Cache] ❌ NLG MISS: ${actionType}/${slot || 'general'} (misses: ${this.nlgMisses})`);
            return null;
        } catch (error) {
            console.error('[Cache] Error getting NLG cache:', error);
            return null;
        }
    }

    /**
     * Set NLG cache
     */
    async setNLGCache(actionType: string, response: string, slot?: string, context?: any): Promise<void> {
        try {
            const contextKey = slot || JSON.stringify(context || {});
            const key = `nlg:${actionType}:${this.hash(contextKey)}`;
            await this.client.set(key, response, 'EX', this.ttl);
            console.log(`[Cache] 💾 NLG SET: ${actionType}/${slot || 'general'}`);
        } catch (error) {
            console.error('[Cache] Error setting NLG cache:', error);
        }
    }

    /**
     * Invalidate all cache (when LLM model changes)
     */
    async invalidateAll(): Promise<number> {
        try {
            const nluKeys = await this.client.keys('nlu:*');
            const nlgKeys = await this.client.keys('nlg:*');

            let deleted = 0;
            for (const key of [...nluKeys, ...nlgKeys]) {
                await this.client.del(key);
                deleted++;
            }

            // Reset counters
            this.nluHits = 0;
            this.nluMisses = 0;
            this.nlgHits = 0;
            this.nlgMisses = 0;

            console.log(`[Cache] 🗑️  Invalidated ${deleted} entries`);
            return deleted;
        } catch (error) {
            console.error('[Cache] Error invalidating cache:', error);
            return 0;
        }
    }

    /**
     * Get cache statistics
     */
    async getStats(): Promise<{
        nluEntries: number;
        nlgEntries: number;
        nluHitRate: number;
        nlgHitRate: number;
        totalHits: number;
        totalMisses: number;
        overallHitRate: number;
    }> {
        try {
            const nluKeys = await this.client.keys('nlu:*');
            const nlgKeys = await this.client.keys('nlg:*');

            const totalHits = this.nluHits + this.nlgHits;
            const totalMisses = this.nluMisses + this.nlgMisses;
            const totalRequests = totalHits + totalMisses;

            const nluRequests = this.nluHits + this.nluMisses;
            const nlgRequests = this.nlgHits + this.nlgMisses;

            return {
                nluEntries: nluKeys.length,
                nlgEntries: nlgKeys.length,
                nluHitRate: nluRequests > 0 ? (this.nluHits / nluRequests * 100) : 0,
                nlgHitRate: nlgRequests > 0 ? (this.nlgHits / nlgRequests * 100) : 0,
                totalHits,
                totalMisses,
                overallHitRate: totalRequests > 0 ? (totalHits / totalRequests * 100) : 0
            };
        } catch (error) {
            console.error('[Cache] Error getting stats:', error);
            return {
                nluEntries: 0,
                nlgEntries: 0,
                nluHitRate: 0,
                nlgHitRate: 0,
                totalHits: 0,
                totalMisses: 0,
                overallHitRate: 0
            };
        }
    }

    /**
     * Get TTL in seconds
     */
    getTTL(): number {
        return this.ttl;
    }
}
