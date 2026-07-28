/**
 * useAuth Hook
 * 
 * Simple in-memory authentication for internal dashboards.
 * 
 * UPGRADE PATH:
 * For production dashboards, replace this with:
 * - OAuth 2.0 (Google, GitHub, etc.)
 * - SSO integration (Auth0, Supabase Auth, Clerk)
 * - Session-based auth with cookies
 * 
 * See docs/CUSTOMIZATION.md for auth upgrade instructions.
 */

import { useState, createContext, useContext, useEffect } from "react";

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  login: (credentials: any) => boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any | null>(null);

  useEffect(() => {
    // Check for existing auth in localStorage
    const storedAuth = localStorage.getItem("auth");
    if (storedAuth) {
      try {
        const auth = JSON.parse(storedAuth);
        setIsAuthenticated(true);
        setUser(auth);
      } catch (e) {
        localStorage.removeItem("auth");
      }
    }
  }, []);

  const login = (credentials: any) => {
    // In mock mode, any credentials work
    // In production, validate against your auth provider
    setIsAuthenticated(true);
    setUser(credentials);
    localStorage.setItem("auth", JSON.stringify(credentials));
    return true;
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem("auth");
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
