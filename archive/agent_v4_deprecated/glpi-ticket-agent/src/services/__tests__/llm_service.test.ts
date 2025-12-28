import { LLMService } from '../../llm_service';
import { CircuitState } from '../../circuit_breaker';

describe('LLMService - Dual Provider', () => {
    let llmService: LLMService;

    beforeEach(() => {
        llmService = new LLMService();
        // Reset circuit for each test
        llmService.resetCircuit();
    });

    describe('NIM Primary Provider', () => {
        it('should use NIM when circuit is healthy', async () => {
            // This test requires NIM to be running
            // In real env, we'd mock fetch
            const status = llmService.getStatus();
            expect(status.primaryProvider).toBe('NIM');
            expect(status.circuitState).toBe(CircuitState.CLOSED);
        });

        it('should record successful NIM calls', async () => {
            // Mock successful NIM response
            global.fetch = jest.fn().mockResolvedValue({
                ok: true,
                json: async () => ({
                    choices: [{ message: { content: 'Test response' } }]
                })
            }) as any;

            const response = await llmService.complete('Test prompt');
            expect(response).toBe('Test response');

            const status = llmService.getStatus();
            expect(status.consecutiveNimSuccesses).toBeGreaterThan(0);
        });
    });

    describe('Ollama Fallback', () => {
        it('should fallback to Ollama when NIM fails', async () => {
            // Mock NIM failure
            let callCount = 0;
            global.fetch = jest.fn().mockImplementation((url: string) => {
                callCount++;
                if (url.includes('nim-llm')) {
                    return Promise.reject(new Error('NIM down'));
                } else {
                    return Promise.resolve({
                        ok: true,
                        json: async () => ({
                            choices: [{ message: { content: 'Ollama response' } }]
                        })
                    });
                }
            }) as any;

            const response = await llmService.complete('Test prompt');
            expect(response).toBe('Ollama response');
            expect(callCount).toBe(2); // 1 NIM attempt + 1 Ollama fallback
        });
    });

    describe('Circuit Breaker', () => {
        it('should open circuit after 3 consecutive failures', async () => {
            // Mock NIM to always fail
            global.fetch = jest.fn().mockImplementation((url: string) => {
                if (url.includes('nim-llm')) {
                    return Promise.reject(new Error('NIM down'));
                } else {
                    return Promise.resolve({
                        ok: true,
                        json: async () => ({
                            choices: [{ message: { content: 'Ollama response' } }]
                        })
                    });
                }
            }) as any;

            // Make 3 failed calls
            await llmService.complete('Test 1');
            await llmService.complete('Test 2');
            await llmService.complete('Test 3');

            const status = llmService.getStatus();
            expect(status.circuitState).toBe(CircuitState.OPEN);
        });

        it('should use Ollama directly when circuit is open', async () => {
            // Open circuit manually
            global.fetch = jest.fn().mockRejectedValue(new Error('NIM down')) as any;

            // Trigger 3 failures
            await llmService.complete('Fail 1');
            await llmService.complete('Fail 2');
            await llmService.complete('Fail 3');

            // Now mock Ollama to work
            global.fetch = jest.fn().mockResolvedValue({
                ok: true,
                json: async () => ({
                    choices: [{ message: { content: 'Ollama works' } }]
                })
            }) as any;

            const response = await llmService.complete('Test');
            expect(response).toBe('Ollama works');

            // Should have called Ollama directly (only 1 call, no NIM attempt)
            expect(global.fetch).toHaveBeenCalledTimes(1);
        });
    });

    describe('JSON Completion', () => {
        it('should parse valid JSON response', async () => {
            global.fetch = jest.fn().mockResolvedValue({
                ok: true,
                json: async () => ({
                    choices: [{ message: { content: '{"name":"João","age":30}' } }]
                })
            }) as any;

            const result = await llmService.completeJson<{ name: string, age: number }>('Get user info');
            expect(result).toEqual({ name: 'João', age: 30 });
        });

        it('should handle JSON with markdown blocks', async () => {
            global.fetch = jest.fn().mockResolvedValue({
                ok: true,
                json: async () => ({
                    choices: [{ message: { content: '```json\n{"status":"ok"}\n```' } }]
                })
            }) as any;

            const result = await llmService.completeJson<{ status: string }>('Get status');
            expect(result).toEqual({ status: 'ok' });
        });
    });
});
