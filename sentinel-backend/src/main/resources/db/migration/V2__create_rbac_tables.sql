CREATE TABLE IF NOT EXISTS role_permissions (
                                                id         BIGSERIAL PRIMARY KEY,
                                                role       VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN','ANALYST','VIEWER')),
                                                permission VARCHAR(30) NOT NULL CHECK (permission IN (
                                                                                                      'CHAT_ACCESS','DOCUMENT_UPLOAD','KNOWLEDGE_MANAGE','AUDIT_VIEW'
                                                    )),
                                                CONSTRAINT uq_role_permission UNIQUE (role, permission)
);

-- Seed default RBAC mappings
INSERT INTO role_permissions (role, permission) VALUES
                                                    ('ADMIN',   'CHAT_ACCESS'),
                                                    ('ADMIN',   'DOCUMENT_UPLOAD'),
                                                    ('ADMIN',   'KNOWLEDGE_MANAGE'),
                                                    ('ADMIN',   'AUDIT_VIEW'),
                                                    ('ANALYST', 'CHAT_ACCESS'),
                                                    ('ANALYST', 'DOCUMENT_UPLOAD'),
                                                    ('VIEWER',  'CHAT_ACCESS')
ON CONFLICT ON CONSTRAINT uq_role_permission DO NOTHING;