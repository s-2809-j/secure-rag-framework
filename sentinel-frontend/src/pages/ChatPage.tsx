import { useEffect, useRef, useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import ChatMessage from '../components/ChatMessage';
// import type { ChatResponse } from '../types';
import type { ChatResponse, ChatBlockedPayload } from '../types';
interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  blocked?: boolean;
  requestId?: string;
  timestamp?: string;
}

function generateUUID(): string {
  return crypto.randomUUID();
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // One session ID per mount — persists across messages in this session
  const sessionId = useRef<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async () => {
    const q = query.trim();
    if (!q || loading) return;

    if (q.length > 4000) {
      setError('Message is too long. Please keep it under 4000 characters.');
      return;
    }

    setError('');
    setQuery('');

    const userMsg: Message = {
      id: generateUUID(),
      role: 'user',
      text: q,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const { data } = await axiosInstance.post<ChatResponse>('/api/v1/chat', {
        query: q,
        sessionId: sessionId.current ?? undefined,
      });

      // Persist the session ID returned by the backend for all subsequent messages
      if (data.sessionId != null && !sessionId.current) {
        sessionId.current = String(data.sessionId);
      }

      const assistantMsg: Message = {
        id: generateUUID(),
        role: 'assistant',

        // "data" holds the AI answer (string) on success
        // "data" holds a blocked-payload object when blocked
        // "message" is just a status string — never the answer
        text: typeof data.data === 'string'
          ? data.data
          : (data.data as ChatBlockedPayload | null)?.reason
          ?? data.message   // last resort fallback
          ?? '',

        // Blocked when: success=false OR data.data is an object with blocked:true
        blocked: !data.success ||
          (typeof data.data === 'object' &&
            data.data !== null &&
            (data.data as ChatBlockedPayload).blocked === true),

        requestId: data.requestId,
        timestamp: data.timestamp,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 401) {
        setError('Your session has expired. Please log in again.');
      } else if (status === 413) {
        setError('Message is too large. Please shorten your query.');
      } else if (status === 502) {
        setError('AI service is temporarily unavailable. Please try again in a moment.');
      } else {
        setError('Failed to get a response. Please try again.');
      }
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      {/* Header bar */}
      <div className="border-b border-sentinel-border/30 bg-sentinel-dark/50 px-6 py-3 flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-sentinel-success animate-pulse" />
        <span className="text-sentinel-text text-sm font-medium">Secure Chat Session</span>
        <span className="font-mono text-[10px] text-sentinel-muted/60 ml-auto">
          Session: {sessionId.current ? sessionId.current.slice(0, 8) : 'new'}
        </span>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-4xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-sentinel-accent/20 to-violet-500/20 border border-sentinel-border/40 flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-sentinel-accent" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
              </svg>
            </div>
            <h2 className="text-sentinel-light font-semibold text-lg mb-1">
              Sentinel AI Assistant
            </h2>
            <p className="text-sentinel-muted text-sm max-w-sm">
              Ask anything. All queries are screened by the input security agent before processing.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            role={msg.role}
            text={msg.text}
            blocked={msg.blocked}
            requestId={msg.requestId}
            timestamp={msg.timestamp}
          />
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start mb-4 animate-fade-in">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sentinel-accent to-violet-500 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
              </svg>
            </div>
            <div className="glass-card-sm px-4 py-3 rounded-tl-sm">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-sentinel-accent rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-sentinel-accent rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-sentinel-accent rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="px-6 py-2">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-2 bg-sentinel-danger/10 border border-sentinel-danger/30 rounded-xl px-4 py-2.5 text-sentinel-danger text-sm">
              <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        </div>
      )}

      {/* Input bar */}
      <div className="border-t border-sentinel-border/30 bg-sentinel-dark/60 backdrop-blur-sm px-4 py-4">
        <div className="max-w-4xl mx-auto flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              id="chat-input"
              rows={1}
              value={query}
              onKeyDown={handleKeyDown}
              placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
              className="sentinel-input resize-none overflow-hidden leading-relaxed pr-4"
              style={{ minHeight: '48px', maxHeight: '160px' }}
              onChange={(e) => {
                setQuery(e.target.value);
                const el = e.currentTarget;
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 160) + 'px';
              }}
            />
          </div>
          <button
            id="chat-send"
            onClick={sendMessage}
            disabled={loading || !query.trim()}
            className="btn-primary flex items-center gap-2 px-5 py-3 flex-shrink-0"
          >
            {loading ? (
              <span className="spinner w-4 h-4" />
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        <p className="text-center text-sentinel-muted/40 text-[10px] mt-2">
          All messages are encrypted and screened by Sentinel's security agents.
        </p>
      </div>
    </div>
  );
}
