import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, TicketCheck } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { useAuth } from '../contexts/AuthContext';  // ← Importar AuthContext
import ChatMessage from './ChatMessage';

export default function ChatWindow() {
    const { user } = useAuth();  // ← Obter userId do contexto
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { messages, isLoading, ticketId, sendUserMessage, handleFormSubmit } = useChat(user?.id);

    // Auto-scroll para última mensagem
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        sendUserMessage(input.trim());
        setInput('');
    };

    return (
        <div className="h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100">
            {/* ... Header ... */}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 chat-scrollbar">
                <div className="max-w-3xl mx-auto space-y-4">
                    {/* ... Empty State ... */}
                    {messages.length === 0 && (
                        <div className="text-center py-12">
                            {/* ... */}
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <ChatMessage
                            key={index}
                            message={message}
                            onFormSubmit={handleFormSubmit}
                        />
                    ))}

                    {isLoading && (
                        <div className="flex items-center gap-2 text-slate-600">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span className="text-sm">O assistente está digitando...</span>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input */}
            <div className="border-t border-slate-200 px-6 py-4 bg-white">
                <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Digite sua mensagem..."
                            className="flex-1 px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                        >
                            <Send className="w-5 h-5" />
                            Enviar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
