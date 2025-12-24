import fetch from 'node-fetch';
import { configManager, LLMProviderConfig } from '../config';
import { jsonrepair } from 'jsonrepair';
import { CircuitBreaker } from './circuit_breaker';

/**
 * LLM Service with Dual Provider Support (NIM + Ollama)
 * 
 * Features:
 * - NIM as primary provider (low latency, GPU-optimized)
 * - Ollama as fallback (reliable, always available)
 * - Circuit breaker pattern to prevent cascading failures
 * - Automatic health checking and recovery
 */

export class LLMService {
    private config = configManager.getLLMConfig();
    private circuitBreaker: CircuitBreaker;
    private consecutiveNimSuccesses: number = 0;

    constructor() {
        this.circuitBreaker = new CircuitBreaker({
            failureThreshold: 3,
            recoveryTimeoutMs: 5 * 60 * 1000, // 5 minutes
            successThreshold: 2
        });

        console.log('[LLMService] Initialized with dual provider (NIM + Ollama)');
    }

    /**
     * Completes a prompt using the configured LLM (with automatic fallback).
     * Returns the raw string response.
     */
    async complete(prompt: string, systemPrompt?: string): Promise<string> {
        const sys = systemPrompt || "You are a helpful assistant.";

        // Try NIM first if circuit is healthy
        if (this.circuitBreaker.isHealthy()) {
            try {
                const startTime = Date.now();
                const response = await this.callProvider(
                    this.config.nim,
                    prompt,
                    sys
                );
                const latency = Date.now() - startTime;

                console.log(`[LLMService] ✅ NIM successful (${latency}ms)`);
                this.circuitBreaker.recordSuccess();
                this.consecutiveNimSuccesses++;

                return response;

            } catch (error) {
                console.warn('[LLMService] ❌ NIM failed:', (error as Error).message);
                this.circuitBreaker.recordFailure();

                // Fallback to Ollama if enabled
                if (this.config.fallbackEnabled) {
                    console.log('[LLMService] 🔄 Falling back to Ollama...');
                    return await this.callOllamaFallback(prompt, sys);
                } else {
                    throw error; // Re-throw if fallback disabled
                }
            }
        } else {
            // Circuit is open, use Ollama directly
            const circuitState = this.circuitBreaker.getState();
            console.log(`[LLMService] ⚠️ Circuit ${circuitState.state}, using Ollama directly`);
            return await this.callOllamaFallback(prompt, sys);
        }
    }

    /**
     * Call Ollama as fallback provider
     */
    private async callOllamaFallback(prompt: string, systemPrompt: string): Promise<string> {
        try {
            const startTime = Date.now();
            const response = await this.callProvider(
                this.config.ollama,
                prompt,
                systemPrompt
            );
            const latency = Date.now() - startTime;

            console.log(`[LLMService] ✅ Ollama fallback successful (${latency}ms)`);
            return response;

        } catch (error) {
            console.error('[LLMService] ❌ Ollama fallback also failed:', error);
            return ""; // Return empty string as last resort
        }
    }

    /**
     * Generic provider call (works for both NIM and Ollama)
     */
    private async callProvider(
        provider: LLMProviderConfig,
        prompt: string,
        systemPrompt: string
    ): Promise<string> {
        // Normalize URL: Remove trailing /v1 or / if present to avoid duplication
        const baseUrl = provider.baseUrl.replace(/\/v1\/?$/, '').replace(/\/$/, '');
        const url = `${baseUrl}/v1/chat/completions`;

        const body = {
            model: provider.model,
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: prompt }
            ],
            temperature: this.config.temperature,
            max_tokens: 1024,
            stream: false
        };

        const headers: Record<string, string> = {
            'Content-Type': 'application/json'
        };

        // Add authorization if API key is present (for NIM)
        if (provider.apiKey) {
            headers['Authorization'] = `Bearer ${provider.apiKey}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`LLM API Error ${response.status}: ${errText}`);
        }

        const data = await response.json() as any;

        // OpenAI format
        const content = data.choices?.[0]?.message?.content || "";
        return content.trim();
    }

    /**
     * Completes a prompt and parses the result as JSON.
     * Uses jsonrepair to fix common LLM syntax errors.
     */
    async completeJson<T>(prompt: string, schemaDescription?: string): Promise<T | null> {
        const systemPrompt = `You are a JSON-only API. You must return a valid JSON object matching the requested schema. Do not include markdown blocks like \`\`\`json. Just the raw JSON.
    
    ${schemaDescription ? "Expected Schema:\n" + schemaDescription : ""}
    `;

        const raw = await this.complete(prompt, systemPrompt);
        if (!raw) return null;

        try {
            // Clean up markdown code blocks if present (common Llama artifact)
            let clean = raw.replace(/```json/g, '').replace(/```/g, '').trim();

            // Use jsonrepair to handle missing quotes, trailing commas, etc.
            const parsed = JSON.parse(jsonrepair(clean));
            return parsed as T;
        } catch (e) {
            console.error("[LLMService] JSON Parse Error on:", raw, e);
            return null;
        }
    }

    /**
     * Get current provider status (for monitoring/debugging)
     */
    getStatus(): {
        primaryProvider: string;
        circuitState: string;
        fallbackEnabled: boolean;
        consecutiveNimSuccesses: number;
    } {
        const state = this.circuitBreaker.getState();
        return {
            primaryProvider: 'NIM',
            circuitState: state.state,
            fallbackEnabled: this.config.fallbackEnabled,
            consecutiveNimSuccesses: this.consecutiveNimSuccesses
        };
    }

    /**
     * Manually reset circuit breaker (for testing/admin)
     */
    resetCircuit(): void {
        this.circuitBreaker.reset();
        this.consecutiveNimSuccesses = 0;
        console.log('[LLMService] Circuit breaker manually reset');
    }
}

export const llmService = new LLMService();
