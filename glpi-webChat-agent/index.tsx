import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Send,
  Ticket,
  CheckCircle2,
  AlertCircle,
  Loader2,
  User,
  Bot,
  LayoutDashboard,
  ClipboardList,
  Save,
  Plus,
  Lock,
  LogIn,
  Eye,
  EyeOff
} from 'lucide-react';

// --- Types ---
interface TicketDraft {
  title: string | null;
  description: string | null;
  category: string | null; // problemType in backend
  urgency: string | null;
  location: string | null;
  extension: string | null;
}

interface Message {
  role: 'user' | 'model';
  text: string;
}

interface UserSession {
  userId: string | number;
  token: string;
}

// --- Components ---

const LoginScreen = ({ onLogin }: { onLogin: (u: string, p: string) => Promise<void> }) => {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await onLogin(user, pass);
    } catch (err: any) {
      setError(err.message || 'Falha ao autenticar');
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-slate-900">
      <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-2xl">
        <div className="flex justify-center mb-6">
          <div className="p-3 bg-blue-600 rounded-xl text-white">
            <Lock size={32} />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-center text-slate-800 mb-2">Acesso Restrito</h2>
        <p className="text-center text-slate-500 mb-8">Faça login com sua conta GLPI para acessar o assistente.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Usuário</label>
            <input
              type="text"
              className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={user}
              onChange={e => setUser(e.target.value)}
              placeholder="ex: jonathan"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Senha</label>
            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none pr-10"
                value={pass}
                onChange={e => setPass(e.target.value)}
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              >
                {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm flex items-center gap-2">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" /> : <><LogIn size={18} /> Entrar</>}
          </button>
        </form>
      </div>
    </div>
  );
};

const App = () => {
  const [session, setSession] = useState<UserSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDone, setIsDone] = useState(false);

  // Sidebar State (Live from Backend)
  const [ticket, setTicket] = useState<TicketDraft>({
    title: null,
    description: null,
    category: null,
    urgency: null,
    location: null,
    extension: null
  });

  const [creatingTicket, setCreatingTicket] = useState(false);
  const [ticketId, setTicketId] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleLogin = async (u: string, p: string) => {
    const res = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: u, password: p })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Login falhou');

    setSession({ userId: data.userId, token: data.token });
    // Add initial greeting locally or fetch from history
    setMessages([{ role: 'model', text: `Olá! Sou seu assistente de suporte.Como posso ajudar com seu problema técnico hoje ? ` }]);
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputText.trim() || isLoading || isDone || !session) return;

    const userMessage = inputText.trim();
    setInputText('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          sessionId: `session - ${session.userId} `, // Simple Session ID mapping
          userId: session.userId
        })
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error);

      // 1. Append Agent Response
      setMessages(prev => [...prev, { role: 'model', text: data.response }]);

      // 2. Update Sidebar with Extracted Entities
      if (data.entities) {
        setTicket({
          title: data.entities.description ? (data.entities.description.slice(0, 30) + "...") : null, // Heuristic for title
          description: data.entities.description,
          category: data.entities.problemType, // Mapping problemType -> Category
          urgency: null, // Extractor doesn't extract urgency yet, purely semantic.
          location: data.entities.location,
          extension: data.entities.extension
        });
      }

    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, { role: 'model', text: "Erro ao conectar com o servidor. Tente novamente." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTicket = async () => {
    if (!session || !ticket.description) return;
    setCreatingTicket(true);

    try {
      const res = await fetch('http://localhost:8000/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: session.userId,
          title: ticket.title,
          description: ticket.description,
          category: ticket.category,
          location: ticket.location,
          extension: ticket.extension
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      setTicketId(data.ticketId);
      setIsDone(true);

      // Add system message via UI
      setMessages(prev => [...prev, {
        role: 'model',
        text: `✅ Ticket Criado com Sucesso! ID: ${data.ticketId}\nUm técnico analisará seu problema em breve.`
      }]);

    } catch (err) {
      console.error("Failed to create ticket", err);
      alert("Erro ao criar ticket. Veja o console.");
    } finally {
      setCreatingTicket(false);
    }
  };

  const isTicketComplete = !!(ticket.description && ticket.category && ticket.location);

  if (!session) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="flex flex-col lg:flex-row h-screen w-full bg-slate-50 overflow-hidden font-sans text-slate-900">
      {/* Sidebar - Dashboard View */}
      <aside className="hidden lg:flex flex-col w-72 bg-slate-900 text-white p-5 border-r border-slate-800">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-blue-600 rounded-lg">
            <LayoutDashboard size={20} />
          </div>
          <h1 className="text-lg font-bold tracking-tight">GLPI Agent V2</h1>
        </div>

        <nav className="flex-1 space-y-2">
          <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg text-blue-400 border border-slate-700/50">
            <Plus size={18} />
            <span className="font-medium text-sm">Novo Ticket</span>
          </div>
        </nav>

        <div className="mt-auto pt-4 border-t border-slate-800">
          <div className="flex items-center gap-3 p-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-xs font-bold">
              ID
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium">Usuário {session.userId}</span>
              <span className="text-[10px] text-slate-500">Conectado</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-white relative shadow-xl z-10">
        <header className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div>
              <h2 className="font-bold text-slate-800">Assistente Virtual</h2>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Online via Ollama</span>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-100 text-purple-600'
                  }`}>
                  {m.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-wrap ${m.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-white text-slate-700 border border-slate-200/60 rounded-tl-none'
                  }`}>
                  {m.text}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3 items-center">
                <div className="w-8 h-8 rounded-full bg-white border border-slate-100 flex items-center justify-center text-purple-600">
                  <Loader2 size={16} className="animate-spin" />
                </div>
                <span className="text-xs text-slate-400 italic">Processando resposta...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <footer className="p-4 border-t border-slate-100 bg-white">
          <form onSubmit={handleSendMessage} className="relative flex items-center max-w-4xl mx-auto">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isLoading || isDone}
              placeholder="Descreva seu problema..."
              className="w-full pl-5 pr-14 py-4 bg-slate-100 border-transparent rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium placeholder:text-slate-400"
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isLoading || isDone}
              className="absolute right-2 p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:bg-slate-300 transition-all shadow-lg shadow-blue-600/20 active:scale-95"
            >
              <Send size={18} />
            </button>
          </form>
        </footer>
      </main>

      {/* Right Side - Live Ticket Preview */}
      <aside className="w-full lg:w-80 bg-white border-l border-slate-200 overflow-y-auto">
        <div className="p-6 border-b border-slate-100 bg-slate-50/50">
          <h3 className="font-bold text-slate-800 flex items-center gap-2 text-sm">
            <Ticket className="text-blue-600" size={16} />
            Contexto Extraído
          </h3>
        </div>

        <div className="p-6 space-y-6">
          {/* Status Card */}
          <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
            <div className="text-xs font-bold text-blue-800 mb-2 uppercase tracking-wider">Confiança da IA</div>
            <div className="h-1.5 w-full bg-blue-200 rounded-full overflow-hidden">
              <div className="h-full bg-blue-600 w-[85%]"></div>
            </div>
          </div>

          {/* Fields */}
          <div className="space-y-4">
            <div className="group">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 block">Problema</label>
              <div className="min-h-[20px] text-sm font-medium text-slate-900 border-b border-slate-100 pb-1 group-hover:border-blue-200 transition-colors">
                {ticket.category || <span className="text-slate-300 italic">...</span>}
              </div>
            </div>

            <div className="group">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 block">Local</label>
              <div className="min-h-[20px] text-sm font-medium text-slate-900 border-b border-slate-100 pb-1 group-hover:border-blue-200 transition-colors">
                {ticket.location || <span className="text-slate-300 italic">...</span>}
              </div>
            </div>

            <div className="group">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 block">Ramal</label>
              <div className="min-h-[20px] text-sm font-medium text-slate-900 border-b border-slate-100 pb-1 group-hover:border-blue-200 transition-colors">
                {ticket.extension || <span className="text-slate-300 italic">...</span>}
              </div>
            </div>

            <div className="group">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 block">Resumo</label>
              <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100 min-h-[80px]">
                {ticket.description || <span className="text-slate-300 italic">Aguardando detalhes...</span>}
              </p>
            </div>
          </div>

          <button
            onClick={handleCreateTicket}
            disabled={!isTicketComplete || creatingTicket || isDone}
            className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg transition-all ${isDone
                ? 'bg-green-600 text-white hover:bg-green-700 shadow-green-600/20 cursor-default'
                : isTicketComplete
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-600/20 active:scale-[0.98]'
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
          >
            {creatingTicket ? (
              <> <Loader2 size={18} className="animate-spin" /> Processando... </>
            ) : isDone ? (
              <>
                <CheckCircle2 size={18} /> Enviado #{ticketId}
              </>
            ) : (
              <>
                <Save size={18} /> Abrir Chamado
              </>
            )}
          </button>
        </div>
      </aside>
    </div>
  );
};

createRoot(document.getElementById('root')!).render(<App />);