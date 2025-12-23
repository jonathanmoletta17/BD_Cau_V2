import axios from 'axios';
import type { ChatResponse } from '../types/chat';

const API_BASE_URL = '/api';

const chatApi = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,  // Aumentado para 60s (LLM pode demorar)
    headers: {
        'Content-Type': 'application/json',
    },
});

export async function sendMessage(
    message: string,
    conversationId?: string,
    userId?: string  // ← Novo parâmetro
): Promise<ChatResponse> {
    const { data } = await chatApi.post<ChatResponse>('/chat', {
        message,
        conversationId,
        userId: userId || 'unknown'  // ← Usar userId real ou fallback
    });
    return data;
}

export async function submitForm(
    conversationId: string,
    formData: any,
    userId?: string
): Promise<ChatResponse> {
    const { data } = await chatApi.post<ChatResponse>('/chat/submit', {
        conversationId,
        formData,
        userId: userId || 'unknown'
    });
    return data;
}

export default chatApi;
