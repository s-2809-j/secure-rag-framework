CREATE TABLE IF NOT EXISTS users (
                                     id            UUID  PRIMARY KEY,
                                     username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL CHECK (role IN ('ADMIN','ANALYST','VIEWER')),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    active        BOOLEAN      NOT NULL DEFAULT TRUE
    );

CREATE TABLE IF NOT EXISTS refresh_tokens (
                                              id         BIGSERIAL PRIMARY KEY,
                                              token      VARCHAR(512) NOT NULL UNIQUE,
    user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ  NOT NULL,
    revoked    BOOLEAN      NOT NULL DEFAULT FALSE
    );

CREATE INDEX idx_refresh_tokens_token   ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_users_username         ON users(username);
CREATE INDEX idx_users_email            ON users(email);