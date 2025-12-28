import React, { createContext, useContext, useState, useEffect } from 'react';

/**
 * Interface definition for the User object
 */
export interface User {
    id: string;
    username: string;
    token: string;
}

/**
 * Interface for the AuthContext
 */
interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (userData: User) => void;
    logout: () => void;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component to wrap the application
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    // Load user from localStorage on mount
    useEffect(() => {
        const storedUser = localStorage.getItem('glpi_user');
        if (storedUser) {
            try {
                const parsedUser = JSON.parse(storedUser);
                if (parsedUser && parsedUser.token) {
                    setUser(parsedUser);
                }
            } catch (e) {
                console.error("Failed to parse stored user", e);
                localStorage.removeItem('glpi_user');
            }
        }
        setLoading(false);
    }, []);

    const login = (userData: User) => {
        setUser(userData);
        localStorage.setItem('glpi_user', JSON.stringify(userData));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('glpi_user');
        // Optional: Window reload to clear any other state
        window.location.reload();
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated: !!user,
            login,
            logout,
            loading
        }}>
            {children}
        </AuthContext.Provider>
    );
};

/**
 * Custom hook to use the AuthContext
 */
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
