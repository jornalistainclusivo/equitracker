import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, X, Maximize2, Minimize2, Trash2, Copy, Download, Square, Check } from 'lucide-react';
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
    const [isCopied, setIsCopied] = useState(false);

    const quickPrompts = [
        { label: "🔍 Resumo Executivo", text: "Gere um resumo executivo desta matéria focando nos principais atores e fatos." },
        { label: "⚖️ Checar Viés (LBI)", text: "Analise a matéria sob a ótica da LBI (Lei Brasileira de Inclusão) e identifique possíveis vieses capacitistas." },
        { label: "📜 Contexto Legal", text: "Quais são os marcos legais e direitos humanos citados ou omitidos nesta narrativa?" },
        { label: "💡 Sugerir Pauta Inclusiva", text: "Com base neste texto, sugira pautas complementares que tragam uma perspectiva mais inclusiva e diversa." },
        { label: "🔎 Quem financia?", text: "Existem informações ou pistas sobre o financiamento e interesses econômicos por trás deste veículo ou desta cobertura?" }
    ];

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

    const handleSend = async (e?: React.FormEvent, customText?: string) => {
        e?.preventDefault();
        const textToSend = customText || input;
        if (!textToSend.trim() || isLoading) return;

        const userMessage = textToSend.trim();
        if (!customText) setInput('');
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

    const clearChat = () => {
        if (window.confirm("Tem certeza que deseja limpar todo o histórico desta conversa?")) {
            setMessages([]);
        }
    };

    const copyChat = () => {
        const text = messages.map(m => `${m.role === 'user' ? 'VOCÊ' : 'IA'}:\n${m.content}`).join('\n\n---\n\n');
        navigator.clipboard.writeText(text);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
    };

    const downloadChat = () => {
        const text = `# Análise EquiTracker: ${sourceName}\n\n` +
            messages.map(m => `### ${m.role === 'user' ? 'Usuário' : 'EquiTracker IA'}\n${m.content}`).join('\n\n---\n\n');

        const blob = new Blob([text], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const filename = `analise-${sourceName.toLowerCase().replace(/\s+/g, '-')}.md`;
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
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
                    {/* Toolbar Actions */}
                    <div className="flex items-center gap-1 mr-4 border-r border-white/10 pr-4">
                        <button
                            onClick={(e) => { e.stopPropagation(); clearChat(); }}
                            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
                            title="Limpar Conversa"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); copyChat(); }}
                            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white flex items-center gap-1.5"
                            title="Copiar Texto"
                        >
                            {isCopied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                            {isCopied && <span className="text-[10px] uppercase font-bold text-green-400">Copiado!</span>}
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); downloadChat(); }}
                            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
                            title="Baixar Markdown"
                        >
                            <Download className="w-4 h-4" />
                        </button>
                    </div>

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
                                    <div className="prose prose-sm max-w-none dark:prose-invert prose-p:leading-relaxed prose-pre:bg-gray-800 prose-pre:text-gray-100">
                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                    </div>
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

                    {/* Input Area */}
                    <div className="p-4 bg-white border-t border-gray-100">
                        {/* Quick Prompts */}
                        <div className="max-w-4xl mx-auto w-full mb-3 flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                            {quickPrompts.map((chip, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleSend(undefined, chip.text)}
                                    className="whitespace-nowrap px-3 py-1.5 rounded-full border border-gray-200 text-xs font-medium text-gray-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all flex items-center gap-1.5 shadow-sm"
                                    disabled={isLoading}
                                >
                                    {chip.label}
                                </button>
                            ))}
                        </div>

                        <form onSubmit={handleSend} className="max-w-4xl mx-auto w-full relative">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Envie um comando ou pergunta para o sistema..."
                                className="w-full bg-gray-50 text-gray-900 placeholder-gray-400 border border-gray-200 rounded-xl py-3 pl-5 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm resize-none min-h-[48px] max-h-[120px]"
                                rows={1}
                                disabled={isLoading}
                            />
                            <button
                                type="submit"
                                disabled={(!input.trim() && !isLoading) || (isLoading && false)} // Button is always active if loading to show "Stop"
                                className={`absolute right-2 bottom-3 p-2 rounded-lg transition-all ${!input.trim() && !isLoading
                                    ? 'text-gray-300 cursor-not-allowed'
                                    : isLoading
                                        ? 'bg-red-500 text-white hover:bg-red-600 shadow-sm'
                                        : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                                    }`}
                            >
                                {isLoading ? <Square className="w-4 h-4 fill-current" /> : <Send className="w-4 h-4" />}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatConsole;
