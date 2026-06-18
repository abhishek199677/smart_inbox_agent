CREATE TABLE IF NOT EXISTS tickets (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) UNIQUE NOT NULL,
    task            TEXT NOT NULL,
    category        VARCHAR(32) NOT NULL DEFAULT 'general',
    response        TEXT,
    assigned_agent  VARCHAR(64),
    rag_used        BOOLEAN DEFAULT FALSE,
    status          VARCHAR(16) NOT NULL DEFAULT 'completed',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets (category);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_session_id ON tickets (session_id);

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id              SERIAL PRIMARY KEY,
    category        VARCHAR(32) NOT NULL,
    title           VARCHAR(256),
    content         TEXT NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_documents (category);
