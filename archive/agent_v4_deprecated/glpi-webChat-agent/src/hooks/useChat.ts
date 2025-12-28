import { useState } from 'react';
import { sendMessage } from '../api/chat';
import type { Message, ChatResponse } from '../types/chat';

export function useChat(userId?: string) {  // ← Aceitar userId
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | undefined>();
    const [ticketId, setTicketId] = useState<string | undefined>();

    const sendUserMessage = async (content: string) => {
        // Adicionar mensagem do usuário
        const userMessage: Message = {
            role: 'user',
            content,
            timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Enviar para API com userId
            const response: ChatResponse = await sendMessage(
                content,
                conversationId,
                userId  // ← Passar userId real
            );

            // Atualizar conversationId
            if (!conversationId) {
                setConversationId(response.conversationId);
            }

            // Adicionar mensagem do assistente
            const assistantMessage: Message = {
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
                type: response.type || 'TEXT',
                metadata: response.metadata
            };
            setMessages((prev) => [...prev, assistantMessage]);

            // Se ticket criado, armazenar ID
            if (response.ticketId) {
                setTicketId(response.ticketId);
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);

            // Mensagem de erro
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Desculpe, ocorreu um erro. Por favor, tente novamente.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFormSubmit = async (data: any) => {
        if (!conversationId) return;
        setIsLoading(true);

        try {
            const response = await import('../api/chat').then(m => m.submitForm(conversationId, data, userId));

            const assistanceMessage: Message = {
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
                type: response.type || 'TEXT',
                metadata: response.metadata
            };
            setMessages(prev => [...prev, assistanceMessage]);

            if (response.ticketId) setTicketId(response.ticketId);

        } catch (error) {
            console.error("Form Submit Error", error);
        } finally {
            setIsLoading(false);
        }
    };

    const resetChat = () => {
        setMessages([]);
        setConversationId(undefined);
        setTicketId(undefined);
    };

    return {
        messages,
        isLoading,
        ticketId,
        sendUserMessage,
        handleFormSubmit, // Exporting new function
        resetChat,
    };
}
