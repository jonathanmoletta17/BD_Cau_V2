import request from 'supertest';
import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';

/**
 * Teste E2E: Multi-Turn Conversation (Incident)
 * 
 * Cenário: Usuário reporta problema com impressora e agente conduz diagnóstico estruturado
 */

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:4000';
const CONVERSATION_ID = `test-multi-turn-${Date.now()}`;

describe('Multi-Turn Incident Flow', () => {
    let app: any;

    beforeAll(async () => {
        // Aguardar backend estar pronto
        await new Promise(resolve => setTimeout(resolve, 2000));
    });

    it('should conduct structured diagnostic conversation', async () => {
        // =======================================================================
        // Turn 1: Usuário reporta problema
        // =======================================================================
        const turn1 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Minha impressora HP não está imprimindo',
                sessionId: 'test-session',
                conversationId: CONVERSATION_ID
            });

        expect(turn1.status).toBe(200);
        expect(turn1.body.type).toBe('TEXT');

        // Deve classificar como INCIDENT
        expect(turn1.body.metadata?.intent).toBe('INCIDENT');

        // Deve fazer primeira pergunta estruturada
        expect(turn1.body.message).toMatch(/modelo|marca|tipo/i);

        console.log('[Turn 1] Agente:', turn1.body.message);

        // =======================================================================
        // Turn 2: Usuário responde primeira pergunta
        // =======================================================================
        const turn2 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'É uma HP LaserJet 1200',
                sessionId: 'test-session',
                conversationId: CONVERSATION_ID
            });

        expect(turn2.status).toBe(200);
        expect(turn2.body.type).toBe('TEXT');

        // Deve fazer segunda pergunta
        expect(turn2.body.message).toMatch(/ligada|conectada|cabo/i);

        console.log('[Turn 2] Agente:', turn2.body.message);

        // =======================================================================
        // Turn 3: Usuário responde segunda pergunta
        // =======================================================================
        const turn3 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Sim, está ligada e conectada por USB',
                sessionId: 'test-session',
                conversationId: CONVERSATION_ID
            });

        expect(turn3.status).toBe(200);
        expect(turn3.body.type).toBe('TEXT');

        // Deve fazer terceira pergunta (erro)
        expect(turn3.body.message).toMatch(/erro|mensagem|problema/i);

        console.log('[Turn 3] Agente:', turn3.body.message);

        // =======================================================================
        // Turn 4: Usuário responde terceira pergunta
        // =======================================================================
        const turn4 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Papel preso na bandeja',
                sessionId: 'test-session',
                conversationId: CONVERSATION_ID
            });

        expect(turn4.status).toBe(200);
        expect(turn4.body.type).toBe('TEXT');

        // Após 3 perguntas, deve oferecer resumo e solução
        expect(turn4.body.message).toMatch(/resumo|solução|ticket/i);

        // Deve perguntar se quer criar ticket
        expect(turn4.body.message).toMatch(/sim|confirmar/i);

        console.log('[Turn 4] Agente:', turn4.body.message);

        // =======================================================================
        // Turn 5: Usuário confirma criação de ticket
        // =======================================================================
        const turn5 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Sim, pode criar o ticket',
                sessionId: 'test-session',
                conversationId: CONVERSATION_ID
            });

        expect(turn5.status).toBe(200);
        expect(turn5.body.type).toBe('TEXT');

        // Deve confirmar criação do ticket
        expect(turn5.body.message).toMatch(/ticket|criado|sucesso/i);

        // Deve ter ticketId no metadata (mock)
        expect(turn5.body.metadata?.ticketId).toBeDefined();

        console.log('[Turn 5] Agente:', turn5.body.message);
        console.log('[Turn 5] TicketId:', turn5.body.metadata?.ticketId);
    });

    it('should handle topic change during diagnostic', async () => {
        const CONV_ID_2 = `test-topic-change-${Date.now()}`;

        // Turn 1: Reportar problema
        const turn1 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Internet não funciona',
                sessionId: 'test-session-2',
                conversationId: CONV_ID_2
            });

        expect(turn1.status).toBe(200);
        expect(turn1.body.metadata?.intent).toBe('INCIDENT');

        // Turn 2: Mudar completamente de tópico
        const turn2 = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Criar usuário João da SECOM',
                sessionId: 'test-session-2',
                conversationId: CONV_ID_2
            });

        expect(turn2.status).toBe(200);

        // Deve detectar mudança de tópico e reclassificar como SERVICE_REQUEST
        expect(turn2.body.metadata?.intent).toBe('SERVICE_REQUEST');
        expect(turn2.body.type).toBe('FORM');

        console.log('[Topic Change] Intent mudou para:', turn2.body.metadata?.intent);
    });

    it('should handle negation and correction', async () => {
        const CONV_ID_3 = `test-correction-${Date.now()}`;

        // Simular fluxo até confirmação
        const createRequest = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Criar usuário Pedro da Casa Militar',
                sessionId: 'test-session-3',
                conversationId: CONV_ID_3
            });

        expect(createRequest.status).toBe(200);

        // Negar e corrigir
        const correction = await request(BASE_URL)
            .post('/chat')
            .send({
                message: 'Não, o nome é Pedro Silva',
                sessionId: 'test-session-3',
                conversationId: CONV_ID_3
            });

        expect(correction.status).toBe(200);

        // Deve manter tipo FORM e solicitar nova confirmação
        expect(correction.body.type).toMatch(/TEXT|FORM/);

        console.log('[Correction] Response:', correction.body.message);
    });

    afterAll(async () => {
        // Cleanup se necessário
    });
});
