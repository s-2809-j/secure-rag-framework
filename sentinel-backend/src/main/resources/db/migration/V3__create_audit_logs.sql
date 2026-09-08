CREATE TABLE IF NOT EXISTS audit_logs (
                                          id         BIGSERIAL PRIMARY KEY,
                                          user_id    UUID       REFERENCES users (id) ON DELETE SET NULL,
                                          action     VARCHAR(100) NOT NULL,
                                          endpoint   VARCHAR(200) NOT NULL,
                                          request_id VARCHAR(100),
                                          ip_address VARCHAR(45),
                                          status_code INTEGER,
                                          timestamp  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                                          details    TEXT
);

CREATE INDEX idx_audit_logs_user_id   ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action    ON audit_logs(action);