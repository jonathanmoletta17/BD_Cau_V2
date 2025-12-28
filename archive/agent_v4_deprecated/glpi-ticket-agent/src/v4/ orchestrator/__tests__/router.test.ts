import { RouterService } from '../../orchestrator/router';
import { LLMService } from '../../../services/llm_service';

describe('RouterService - Intent Classification', () => {
    let router: RouterService;
    let llmService: LLMService;

    beforeEach(() => {
        llmService = new LLMService();
        router = new RouterService(llmService);
    });

    describe('SERVICE_REQUEST Classification', () => {
        it('should classify "Criar usuário João" as SERVICE_REQUEST', async () => {
            const intent = await router.classify('Criar usuário João', []);
            expect(intent).toBe('SERVICE_REQUEST');
        });

        it('should classify "Preciso de acesso para Maria" as SERVICE_REQUEST', async () => {
            const intent = await router.classify('Preciso de acesso para Maria', []);
            expect(intent).toBe('SERVICE_REQUEST');
        });

        it('should classify "Usuário para Pedro da SECOM" as SERVICE_REQUEST', async () => {
            const intent = await router.classify('Usuário para Pedro da SECOM', []);
            expect(intent).toBe('SERVICE_REQUEST');
        });
    });

    describe('INCIDENT Classification', () => {
        it('should classify "Impressora não funciona" as INCIDENT', async () => {
            const intent = await router.classify('Impressora não funciona', []);
            expect(intent).toBe('INCIDENT');
        });

        it('should classify "Internet lenta" as INCIDENT', async () => {
            const intent = await router.classify('Internet lenta', []);
            expect(intent).toBe('INCIDENT');
        });

        it('should classify "Esqueci minha senha" as INCIDENT', async () => {
            const intent = await router.classify('Esqueci minha senha', []);
            expect(intent).toBe('INCIDENT');
        });
    });

    describe('CHITCHAT Classification', () => {
        it('should classify "Como criar um usuário?" as CHITCHAT (question)', async () => {
            const intent = await router.classify('Como criar um usuário?', []);
            expect(intent).toBe('CHITCHAT');
        });

        it('should classify "Olá" as CHITCHAT', async () => {
            const intent = await router.classify('Olá', []);
            expect(intent).toBe('CHITCHAT');
        });

        it('should classify "Obrigado" as CHITCHAT', async () => {
            const intent = await router.classify('Obrigado', []);
            expect(intent).toBe('CHITCHAT');
        });
    });

    describe('Fallback Behavior', () => {
        it('should use keyword fallback when LLM returns invalid response', async () => {
            // Mock LLM to return garbage
            jest.spyOn(llmService, 'complete').mockResolvedValue('INVALID_INTENT_123');

            const intent = await router.classify('Criar usuário Ana', []);

            // Should still classify correctly using fallback
            expect(intent).toBe('SERVICE_REQUEST');
        });

        it('should handle LLM failure gracefully', async () => {
            // Mock LLM to throw error
            jest.spyOn(llmService, 'complete').mockRejectedValue(new Error('LLM timeout'));

            const intent = await router.classify('Impressora não imprime', []);

            // Should use keyword fallback and classify correctly
            expect(intent).toBe('INCIDENT');
        });
    });
});
