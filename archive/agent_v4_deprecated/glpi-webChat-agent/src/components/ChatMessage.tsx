
import { Bot, User } from 'lucide-react';
import type { Message, FormSchema } from '../types/chat';
import DynamicForm from './DynamicForm';

interface ChatMessageProps {
    message: Message;
    onFormSubmit?: (data: any) => void;
}

export default function ChatMessage({ message, onFormSubmit }: ChatMessageProps) {
    const isUser = message.role === 'user';
    const isForm = message.type === 'FORM' && message.metadata?.form;

    return (
        <div
            className={`flex gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'
                }`}
        >
            {/* Avatar */}
            <div
                className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-200 text-slate-700'
                    }`}
            >
                {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
            </div>

            {/* Message Bubble */}
            <div
                className={`max-w-md px-4 py-3 rounded-2xl ${isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-900'
                    }`}
            >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                </p>

                {/* Dynamic Form Rendering */}
                {isForm && (
                    <DynamicForm
                        schema={message.metadata.form as FormSchema}
                        onSubmit={onFormSubmit || ((data) => console.log('Form Submit (No Handler):', data))}
                    />
                )}

                {message.timestamp && (
                    <p
                        className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-slate-500'
                            }`}
                    >
                        {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
                            hour: '2-digit',
                            minute: '2-digit',
                        })}
                    </p>
                )}
            </div>
        </div>
    );
}
