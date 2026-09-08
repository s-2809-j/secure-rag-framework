interface ChatMessageProps {
  role: 'user' | 'assistant';
  text: string;
  blocked?: boolean;
  requestId?: string;
  timestamp?: string;
}

export default function ChatMessage({
  role,
  text,
  blocked,
  requestId,
  timestamp,
}: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-slide-up`}>
      {/* Avatar — assistant only */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sentinel-accent to-violet-500 flex items-center justify-center mr-3 mt-1 flex-shrink-0 shadow-accent">
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
          </svg>
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        {/* Bubble */}
        {blocked ? (
          <div className="blocked-banner">
            <span className="text-lg">⚠</span>
            <div>
              <p className="font-semibold text-sentinel-warning">Message Blocked</p>
              <p className="text-sentinel-warning/80 text-xs mt-0.5">
                This query was flagged by the security agent and blocked.
              </p>
            </div>
          </div>
        ) : (
          <div
            className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              isUser
                ? 'bg-sentinel-accent text-sentinel-dark font-medium rounded-tr-sm'
                : 'glass-card-sm text-sentinel-text rounded-tl-sm'
            }`}
          >
            {text}
          </div>
        )}

        {/* Metadata — assistant messages only */}
        {!isUser && (requestId || timestamp) && (
          <div className="flex items-center gap-3 px-1">
            {requestId && (
              <span className="font-mono text-[10px] text-sentinel-muted/60" title="Request ID">
                #{requestId.slice(0, 8)}
              </span>
            )}
            {timestamp && (
              <span className="text-[10px] text-sentinel-muted/60">
                {new Date(timestamp).toLocaleTimeString()}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Avatar — user only */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-sentinel-surface border border-sentinel-border flex items-center justify-center ml-3 mt-1 flex-shrink-0">
          <svg className="w-4 h-4 text-sentinel-muted" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z" />
          </svg>
        </div>
      )}
    </div>
  );
}
