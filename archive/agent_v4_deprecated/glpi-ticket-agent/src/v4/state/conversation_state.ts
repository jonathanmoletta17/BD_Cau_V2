/**
 * Conversation State Management
 * Mantém estado de conversas para modo de confirmação e interações multi-turn
 */

export interface ConversationState {
    conversationId: string;
    userId: string;
    currentStep: 'initial' | 'awaiting_confirmation' | 'awaiting_correction' | 'processing';
    pendingConfirmation?: {
        data: {
            name?: string;
            entity?: string;
            entityId?: number;
            jobTitle?: string;
            email?: string;
            phone?: string;
        };
        intent: 'SERVICE_REQUEST' | 'INCIDENT';
        requestedAt: string;
    };
    history: Array<{
        role: 'user' | 'agent';
        message: string;
        timestamp: string;
    }>;
    metadata: {
        createdAt: string;
        lastActivityAt: string;
        turnCount: number;
    };
    // Campo genérico para dados customizados por intent
    customData?: Record<string, any>;
}

export class ConversationStateManager {
    constructor(private redis: any) { }

    /**
     * Obtém ou cria estado de conversa
     */
    async getOrCreate(conversationId: string, userId: string): Promise<ConversationState> {
        const key = `conversation:state:${conversationId}`;
        const existing = await this.redis.get(key);

        if (existing) {
            return JSON.parse(existing);
        }

        // Criar novo estado
        const newState: ConversationState = {
            conversationId,
            userId,
            currentStep: 'initial',
            history: [],
            metadata: {
                createdAt: new Date().toISOString(),
                lastActivityAt: new Date().toISOString(),
                turnCount: 0
            }
        };

        await this.save(newState);
        return newState;
    }

    /**
     * Salva estado
     */
    async save(state: ConversationState): Promise<void> {
        const key = `conversation:state:${state.conversationId}`;

        // Atualizar timestamp
        state.metadata.lastActivityAt = new Date().toISOString();

        // Salvar com TTL de 1 hora
        await this.redis.setex(key, 3600, JSON.stringify(state));
    }

    /**
     * Adiciona mensagem ao histórico
     */
    addMessage(state: ConversationState, role: 'user' | 'agent', message: string): void {
        state.history.push({
            role,
            message,
            timestamp: new Date().toISOString()
        });

        if (role === 'user') {
            state.metadata.turnCount++;
        }
    }

    /**
     * Define pendência de confirmação
     */
    setPendingConfirmation(
        state: ConversationState,
        data: {
            name?: string;
            entity?: string;
            entityId?: number;
            jobTitle?: string;
            email?: string;
            phone?: string;
        },
        intent: 'SERVICE_REQUEST' | 'INCIDENT'
    ): void {
        state.currentStep = 'awaiting_confirmation';
        state.pendingConfirmation = {
            data,
            intent,
            requestedAt: new Date().toISOString()
        };
    }

    /**
     * Limpa pendência de confirmação
     */
    clearPendingConfirmation(state: ConversationState): void {
        state.currentStep = 'initial';
        delete state.pendingConfirmation;
    }

    /**
     * Verifica se mensagem é confirmação
     */
    isConfirmation(message: string): boolean {
        const lower = message.toLowerCase().trim();
        const confirmWords = ['sim', 's', 'confirmar', 'confirmo', 'ok', 'yes', 'correto', 'certo'];
        return confirmWords.some(word => lower === word || lower.startsWith(word + ' '));
    }

    /**
     * Verifica se mensagem é negação/correção
     */
    isNegation(message: string): boolean {
        const lower = message.toLowerCase().trim();
        const negationWords = ['não', 'nao', 'n', 'negar', 'nego', 'no', 'errado', 'incorreto'];
        return negationWords.some(word => lower === word || lower.startsWith(word + ' '));
    }

    /**
     * Extrai campo a corrigir da mensagem
     */
    extractCorrectionField(message: string): { field: string; value: string } | null {
        const lower = message.toLowerCase();

        // Patterns de correção
        const patterns = [
            { regex: /nome\s+(?:é|eh|:)\s*(.+)/i, field: 'name' },
            { regex: /(?:órgão|orgao|entidade)\s+(?:é|eh|:)\s*(.+)/i, field: 'entity' },
            { regex: /cargo\s+(?:é|eh|:)\s*(.+)/i, field: 'jobTitle' },
            { regex: /email\s+(?:é|eh|:)\s*(.+)/i, field: 'email' },
        ];

        for (const pattern of patterns) {
            const match = message.match(pattern.regex);
            if (match) {
                return {
                    field: pattern.field,
                    value: match[1].trim()
                };
            }
        }

        return null;
    }

    /**
     * Formata dados para confirmação
     */
    formatConfirmationMessage(data: {
        name?: string;
        entity?: string;
        entityId?: number;
        jobTitle?: string;
        email?: string;
        phone?: string;
    }): string {
        const lines = ['Por favor, confirme os dados:'];

        if (data.name) {
            lines.push(`📝 **Nome:** ${data.name}`);
        }

        if (data.entity) {
            lines.push(`🏢 **Órgão:** ${data.entity}`);
        }

        if (data.jobTitle) {
            lines.push(`💼 **Cargo:** ${data.jobTitle}`);
        }

        if (data.email) {
            lines.push(`📧 **Email:** ${data.email}`);
        }

        if (data.phone) {
            lines.push(`📱 **Telefone:** ${data.phone}`);
        }

        lines.push('');
        lines.push('**Está correto?** (Responda "Sim" para confirmar ou indique o que está errado)');

        return lines.join('\n');
    }

    /**
     * Deleta estado (limpar após conclusão)
     */
    async delete(conversationId: string): Promise<void> {
        const key = `conversation:state:${conversationId}`;
        await this.redis.del(key);
    }
}
