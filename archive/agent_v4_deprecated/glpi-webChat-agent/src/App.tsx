import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import ChatWindow from './components/ChatWindow';

const AppContent: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth();

    if (!isAuthenticated) {
        return <LoginPage />;
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col h-screen">
            {/* Header with user info and logout */}
            <header className="bg-white shadow-sm border-b shrink-0">
                <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-semibold text-sm">
                                {user?.username.charAt(0).toUpperCase()}
                            </span>
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-gray-800">
                                Agente Inteligente
                            </h1>
                            <p className="text-xs text-gray-600">
                                Logado como: {user?.username}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="text-sm text-red-600 hover:text-red-700 font-medium px-4 py-2 rounded-lg hover:bg-red-50 transition-colors border border-red-100"
                    >
                        Sair
                    </button>
                </div>
            </header>

            {/* Chat Area - Flex Grow to fill remaining space */}
            <main className="flex-grow overflow-hidden flex flex-col max-w-5xl mx-auto w-full py-4 px-4">
                <ChatWindow />
            </main>
        </div>
    );
};

function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}

export default App;
