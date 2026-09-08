import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { initAxiosAuth } from '../api/axiosInstance';
import type { AuthUser, LoginResponse } from '../types';

// ─── Context shape ────────────────────────────────────────────────────────────

interface AuthContextValue {
  user: AuthUser | null;
  /** Ref that always reflects current user — safe to read inside Axios interceptors */
  userRef: React.MutableRefObject<AuthUser | null>;
  login: (response: LoginResponse) => void;
  logout: () => void;
  updateTokens: (response: LoginResponse) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const stored = localStorage.getItem('sentinel_user');
      return stored ? (JSON.parse(stored) as AuthUser) : null;
    } catch {
      return null;
    }
  });
  const userRef = useRef<AuthUser | null>(
    (() => {
      try {
        const stored = localStorage.getItem('sentinel_user');
        return stored ? (JSON.parse(stored) as AuthUser) : null;
      } catch {
        return null;
      }
    })()
  );
  // Wire Axios interceptors once at mount time.
  // Must run before any API call is made.
  useEffect(() => {
    initAxiosAuth(
      userRef,
      updateTokens,
      logout,
      (path) => window.location.href = path,
    );
  }, []); // eslint-disable-line react-hooks/exhaustive-deps


  const setUserBoth = useCallback((next: AuthUser | null) => {
    userRef.current = next;
    setUser(next);
    if (next) {
      // NOTE: localStorage is used here for demo simplicity.
      // Production hardening: store only non-sensitive fields here;
      // move access/refresh tokens to HttpOnly cookies set by the backend.
      localStorage.setItem('sentinel_user', JSON.stringify(next));
    } else {
      localStorage.removeItem('sentinel_user');
    }
  }, []);

  const login = useCallback((response: LoginResponse) => {
    setUserBoth({
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      username: response.username,
      role: response.role,
    });
  }, [setUserBoth]);

  const logout = useCallback(() => {
    setUserBoth(null);
  }, [setUserBoth]);

  const updateTokens = useCallback((response: LoginResponse) => {
    setUserBoth({
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      username: response.username,
      role: response.role,
    });
  }, [setUserBoth]);

  return (
    <AuthContext.Provider value={{ user, userRef, login, logout, updateTokens }}>
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
