import { useState } from 'react';
import { motion } from 'motion/react';
import { Lock, User, Eye, EyeOff, Shield, MessageSquare } from 'lucide-react';

export default function App() {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    usuario: '',
    senha: '',
    lembrar: false,
  });
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8003/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.usuario,
          password: formData.senha,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Falha na autenticação');
      }

      console.log('Login success:', data);
      // Here you would redirect or set global state
      console.log('Login success:', data);

      // Show success state briefly before redirect
      // We can use a toast or just redirect immediately
      // precisei adicionar type any para evitar erro de build rapido, ideal seria tipsr o window se necessario
      window.location.href = 'http://localhost:8001';

    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gray-950">
      {/* Left Panel - Branding & Information */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-950 via-gray-900 to-gray-950 relative overflow-hidden"
      >
        {/* Animated background elements */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-72 h-72 bg-blue-600/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl animate-pulse delay-700" />
        </div>

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 opacity-5">
          <div className="grid grid-cols-8 grid-rows-8 h-full w-full">
            {Array.from({ length: 64 }).map((_, i) => (
              <div key={i} className="border border-white/20" />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center p-12 text-white w-full">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="flex items-center gap-3 mb-16"
            >
              <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <Shield className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">DTIC</h1>
                <p className="text-sm text-gray-400">Casa Civil - Rio Grande do Sul</p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="mb-12"
            >
              <h2 className="text-4xl font-bold mb-6 leading-tight">
                Central de<br />
                Atendimento ao<br />
                Usuário - CAU
              </h2>
              <p className="text-lg text-gray-300 max-w-md">
                Acesse o chat de atendimento para abrir e acompanhar seus chamados no sistema GLPI.
              </p>
            </motion.div>

            {/* Chat Icon Feature */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="inline-flex items-center gap-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl px-6 py-4"
            >
              <div className="p-2 bg-blue-600/20 rounded-lg">
                <MessageSquare className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">Atendimento via Chat</h3>
                <p className="text-sm text-gray-400">Suporte em tempo real com nossos agentes</p>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="p-3 bg-blue-600 rounded-xl">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div className="text-left">
                <h1 className="text-2xl font-bold text-white">DTIC</h1>
                <p className="text-sm text-gray-400">Casa Civil - RS</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-gray-800">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">Bem-vindo ao CAU</h2>
              <p className="text-gray-400">Faça login para acessar o atendimento</p>
            </div>

            {error && (
              <div className="p-4 mb-4 text-sm text-red-400 bg-red-900/20 border border-red-900/50 rounded-xl">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Usuario Field */}
              <div>
                <label htmlFor="usuario" className="block mb-2 text-sm font-medium text-gray-300">
                  Usuário
                </label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                    <User className="w-5 h-5" />
                  </div>
                  <input
                    id="usuario"
                    type="text"
                    value={formData.usuario}
                    onChange={(e) => setFormData({ ...formData, usuario: e.target.value })}
                    onFocus={() => setFocusedField('usuario')}
                    onBlur={() => setFocusedField(null)}
                    disabled={isLoading}
                    className={`w-full pl-12 pr-4 py-3.5 rounded-xl border-2 transition-all duration-200 outline-none bg-gray-800/50 text-white placeholder:text-gray-500 ${focusedField === 'usuario'
                      ? 'border-blue-500 bg-gray-800/70'
                      : 'border-gray-700 hover:border-gray-600'
                      } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    placeholder="Digite seu usuário"
                    required
                  />
                </div>
              </div>

              {/* Senha Field */}
              <div>
                <label htmlFor="senha" className="block mb-2 text-sm font-medium text-gray-300">
                  Senha
                </label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    id="senha"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.senha}
                    onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
                    onFocus={() => setFocusedField('senha')}
                    onBlur={() => setFocusedField(null)}
                    disabled={isLoading}
                    className={`w-full pl-12 pr-12 py-3.5 rounded-xl border-2 transition-all duration-200 outline-none bg-gray-800/50 text-white placeholder:text-gray-500 ${focusedField === 'senha'
                      ? 'border-blue-500 bg-gray-800/70'
                      : 'border-gray-700 hover:border-gray-600'
                      } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    placeholder="Digite sua senha"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors disabled:opacity-50"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {/* Remember me and Forgot password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={formData.lembrar}
                    onChange={(e) => setFormData({ ...formData, lembrar: e.target.checked })}
                    disabled={isLoading}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0 cursor-pointer disabled:opacity-50"
                  />
                  <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                    Lembrar de mim
                  </span>
                </label>
                <a href="#" className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors">
                  Esqueceu a senha?
                </a>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-medium shadow-lg shadow-blue-600/20 hover:shadow-xl hover:shadow-blue-600/30 hover:from-blue-700 hover:to-blue-800 transition-all duration-200 transform hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Autenticando...
                  </span>
                ) : (
                  'Acessar Atendimento'
                )}
              </button>
            </form>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-gray-800">
              <p className="text-center text-sm text-gray-500">
                Precisa de ajuda?{' '}
                <a href="#" className="text-blue-400 hover:text-blue-300 font-medium">
                  Contate o suporte
                </a>
              </p>
            </div>
          </div>

          {/* Copyright */}
          <p className="text-center text-sm text-gray-600 mt-6">
            © 2025 DTIC - Casa Civil do Estado do Rio Grande do Sul
          </p>
        </motion.div>
      </div>
    </div>
  );
}