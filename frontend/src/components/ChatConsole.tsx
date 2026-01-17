import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, X, Maximize2, Minimize2 } from 'lucide-react';
import api from '../services/api';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface ChatConsoleProps {
    sourceId: string;
    sourceName: string;
    onClose: () => void;
}

const ChatConsole: React.FC<ChatConsoleProps> = ({ sourceId, sourceName, onClose }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [isExpanded, setIsExpanded] = useState(false);

    // Auto-prompt effect when source changes
    useEffect(() => {
        if (sourceId) {
            setMessages([]); // Clear previous messages
            // Auto-prompt starter
            const starterQuestion = "Quais são os principais pontos de viés nesta matéria?";
            // Optional: Immediately trigger this question or just pre-fill it. 
            // The requirement says "automatically pre-fill or trigger". 
            // Triggering it feels more "Agentic".
            handleAutoTrigger(starterQuestion);
        }
    }, [sourceId]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleAutoTrigger = async (question: string) => {
        setMessages([{ role: 'user', content: question }]);
        setIsLoading(true);
        try {
            const response = await api.post('/chat', {
                source_uid: sourceId,
                query: question
            });
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Desculpe, não consegui iniciar a análise automática." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await api.post('/chat', {
                source_uid: sourceId,
                query: userMessage
            });

            setMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Desculpe, ocorreu um erro ao processar sua pergunta." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div
            className={`fixed bottom-0 left-0 right-0 bg-white shadow-2xl border-t border-gray-200 transition-all duration-300 z-50 flex flex-col ${isExpanded ? 'h-[80vh]' : 'h-[400px]'
                }`}
        >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-3 bg-gray-900 text-white shadow-md cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
                <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-blue-500/20 rounded-lg">
                        <Bot className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-sm tracking-wide">Analisando: <span className="text-blue-300">{sourceName}</span></h3>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}
                        className="p-1.5 hover:bg-white/10 rounded-full transition-colors"
                        title={isExpanded ? "Restaurar" : "Expandir"}
                    >
                        {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); onClose(); }}
                        className="p-1.5 hover:bg-red-500/20 hover:text-red-400 rounded-full transition-colors"
                        title="Fechar Console"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Content Area - Split container could be added here if we wanted side-by-side but for now just wide chat */}
            <div className="flex-1 flex overflow-hidden">
                <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full bg-white shadow-sm border-x border-gray-100">

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/50">
                        {messages.length === 0 && !isLoading && (
                            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-3 opacity-60">
                                <Bot className="w-12 h-12 text-gray-300" />
                                <p>Console de Inteligência pronto.</p>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                {msg.role === 'assistant' && (
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-1 shadow-sm border border-blue-200">
                                        <Bot className="w-5 h-5 text-blue-600" />
                                    </div>
                                )}

                                <div className={`max-w-[75%] rounded-2xl px-6 py-4 text-[15px] shadow-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-tr-sm'
                                        : 'bg-white text-gray-800 border border-gray-200 rounded-tl-sm'
                                    }`}>
                                    <p className="whitespace-pre-wrap font-sans">{msg.content}</p>
                                </div>

                                {msg.role === 'user' && (
                                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                                        <User className="w-5 h-5 text-gray-600" />
                                    </div>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex gap-4 justify-start animate-pulse">
                                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-1">
                                    <Bot className="w-5 h-5 text-blue-600" />
                                </div>
                                <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-6 py-4 shadow-sm">
                                    <div className="flex space-x-2">
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 bg-white border-t border-gray-100">
                        <form onSubmit={handleSend} className="max-w-4xl mx-auto w-full relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Envie um comando ou pergunta para o sistema..."
                                className="w-full bg-gray-50 text-gray-900 placeholder-gray-400 border border-gray-200 rounded-xl py-3 pl-5 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
                                disabled={isLoading}
                            />
                            <button
                                type="submit"
                                disabled={!input.trim() || isLoading}
                                className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all ${!input.trim() || isLoading
                                        ? 'text-gray-300 cursor-not-allowed'
                                        : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                                    }`}
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatConsole;
