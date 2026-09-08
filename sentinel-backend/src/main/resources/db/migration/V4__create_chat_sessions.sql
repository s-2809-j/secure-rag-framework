CREATE TABLE IF NOT EXISTS chat_sessions (
                                             id           BIGSERIAL PRIMARY KEY,
                                             user_id      UUID       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                                             session_name VARCHAR(200),
                                             created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                                             updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
                                             id         BIGSERIAL PRIMARY KEY,
                                             session_id BIGINT      NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                                             role       VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant','system')),
                                             content    TEXT        NOT NULL,
                                             timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                             request_id VARCHAR(100)
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp  ON chat_messages(timestamp);