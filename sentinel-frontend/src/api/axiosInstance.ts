import axios from 'axios';
import type { MutableRefObject } from 'react';
import type { AuthUser, LoginResponse } from '../types';

// ─── Factory ──────────────────────────────────────────────────────────────────
// We export a factory so AuthProvider can inject its ref and callbacks once at
// mount time, avoiding stale closures across the lifetime of the SPA.

let _userRef: MutableRefObject<AuthUser | null> | null = null;
let _updateTokens: ((r: LoginResponse) => void) | null = null;
let _logout: (() => void) | null = null;
let _navigate: ((path: string) => void) | null = null;

export function initAxiosAuth(
  userRef: MutableRefObject<AuthUser | null>,
  updateTokens: (r: LoginResponse) => void,
  logout: () => void,
  navigate: (path: string) => void,
) {
  _userRef      = userRef;
  _updateTokens = updateTokens;
  _logout       = logout;
  _navigate     = navigate;
}

// ─── Axios instance ───────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080';

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Request interceptor — attach Bearer token ────────────────────────────────

axiosInstance.interceptors.request.use((config) => {
  const token = _userRef?.current?.accessToken;
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// ─── Response interceptor — silent refresh on 401 ─────────────────────────────

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (reason?: unknown) => void;
}> = [];

function processQueue(error: unknown, token?: string) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token!);
  });
  failedQueue = [];
}

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Not a 401, or it's the refresh endpoint itself → don't retry
    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      originalRequest.url?.includes('/api/v1/auth/refresh')
    ) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // Queue other requests while refresh is in flight
      return new Promise<string>((resolve, reject) => {
  failedQueue.push({ resolve, reject });
}).then((token) => {
  originalRequest.headers['Authorization'] = `Bearer ${token}`;
  return axiosInstance(originalRequest);
});
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = _userRef?.current?.refreshToken;

    if (!refreshToken) {
      isRefreshing = false;
      _logout?.();
      _navigate?.('/login');
      return Promise.reject(error);
    }

    try {
      const { data } = await axios.post<LoginResponse>(
  `${BASE_URL}/api/v1/auth/refresh`,
  { refreshToken },
);

      _updateTokens?.(data);
      processQueue(null, data.accessToken);

      originalRequest.headers['Authorization'] = `Bearer ${data.accessToken}`;
      return axiosInstance(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError);
      _logout?.();
      _navigate?.('/login');
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export default axiosInstance;
