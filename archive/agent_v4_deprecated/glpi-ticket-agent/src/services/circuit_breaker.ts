/**
 * Circuit Breaker Pattern for LLM Provider Health Management
 * 
 * Prevents repeated calls to unhealthy providers by tracking failures
 * and temporarily switching to fallback provider.
 */

export interface CircuitBreakerConfig {
    failureThreshold: number;      // Number of consecutive failures before opening circuit
    recoveryTimeoutMs: number;     // Time before attempting recovery (ms)
    successThreshold: number;      // Consecutive successes needed to close circuit
}

export enum CircuitState {
    CLOSED = 'CLOSED',         // Normal operation
    OPEN = 'OPEN',             // Provider is unhealthy, using fallback
    HALF_OPEN = 'HALF_OPEN'    // Testing if provider recovered
}

export class CircuitBreaker {
    private state: CircuitState = CircuitState.CLOSED;
    private failureCount: number = 0;
    private successCount: number = 0;
    private lastFailureTime: number = 0;
    private config: CircuitBreakerConfig;

    constructor(config?: Partial<CircuitBreakerConfig>) {
        this.config = {
            failureThreshold: config?.failureThreshold || 3,
            recoveryTimeoutMs: config?.recoveryTimeoutMs || 5 * 60 * 1000, // 5 minutes
            successThreshold: config?.successThreshold || 2
        };
    }

    /**
     * Check if primary provider (NIM) is healthy
     */
    isHealthy(): boolean {
        // If circuit is OPEN, check if recovery timeout has passed
        if (this.state === CircuitState.OPEN) {
            const timeSinceFailure = Date.now() - this.lastFailureTime;
            if (timeSinceFailure >= this.config.recoveryTimeoutMs) {
                console.log('[CircuitBreaker] Recovery timeout passed, entering HALF_OPEN state');
                this.state = CircuitState.HALF_OPEN;
                this.successCount = 0;
                return true; // Allow one probe request
            }
            return false; // Still in cooldown
        }

        return true; // CLOSED or HALF_OPEN allows requests
    }

    /**
     * Record a successful request
     */
    recordSuccess(): void {
        this.failureCount = 0;

        if (this.state === CircuitState.HALF_OPEN) {
            this.successCount++;
            console.log(`[CircuitBreaker] Success in HALF_OPEN (${this.successCount}/${this.config.successThreshold})`);

            if (this.successCount >= this.config.successThreshold) {
                console.log('[CircuitBreaker] Provider recovered, closing circuit');
                this.state = CircuitState.CLOSED;
                this.successCount = 0;
            }
        } else if (this.state === CircuitState.OPEN) {
            // Unexpected success while OPEN (shouldn't happen)
            console.warn('[CircuitBreaker] Unexpected success in OPEN state');
            this.state = CircuitState.CLOSED;
        }
    }

    /**
     * Record a failed request
     */
    recordFailure(): void {
        this.failureCount++;
        this.lastFailureTime = Date.now();

        console.log(`[CircuitBreaker] Failure recorded (${this.failureCount}/${this.config.failureThreshold})`);

        if (this.state === CircuitState.HALF_OPEN) {
            // Failed during recovery probe
            console.warn('[CircuitBreaker] Recovery probe failed, reopening circuit');
            this.state = CircuitState.OPEN;
            this.failureCount = 0;
            this.successCount = 0;
        } else if (this.failureCount >= this.config.failureThreshold) {
            console.warn(`[CircuitBreaker] Failure threshold reached, opening circuit for ${this.config.recoveryTimeoutMs / 1000}s`);
            this.state = CircuitState.OPEN;
        }
    }

    /**
     * Get current circuit state for monitoring
     */
    getState(): { state: CircuitState; failureCount: number; successCount: number } {
        return {
            state: this.state,
            failureCount: this.failureCount,
            successCount: this.successCount
        };
    }

    /**
     * Manually reset circuit (for testing/admin purposes)
     */
    reset(): void {
        console.log('[CircuitBreaker] Manual reset');
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        this.successCount = 0;
        this.lastFailureTime = 0;
    }
}
