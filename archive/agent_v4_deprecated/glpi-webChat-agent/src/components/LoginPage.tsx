import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css'; // We will create this CSS file next

const LoginPage: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    // Get API URL from enviroment or default
    const API_URL = '/api';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            console.log(`Authenticating with ${API_URL}/login...`);
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Falha ao realizar login');
            }

            console.log('Login successful:', data);

            // Save to context
            login({
                id: data.userId,
                username: username,
                token: data.token
            });

        } catch (err: any) {
            console.error('Login error:', err);
            setError(err.message || 'Erro ao conectar com o servidor');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <div className="login-header">
                    <h1>GLPI Agent</h1>
                    <p>Faça login para continuar</p>
                </div>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Usuário</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Digite seu usuário"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Senha</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Digite sua senha"
                            required
                            disabled={isLoading}
                        />
                    </div>

                    <button type="submit" className="login-button" disabled={isLoading}>
                        {isLoading ? 'Entrando...' : 'Entrar'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;
