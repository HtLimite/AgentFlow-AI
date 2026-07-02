CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS sys_user (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nickname VARCHAR(64),
  role VARCHAR(32) DEFAULT 'USER',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_model_provider (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  provider_type VARCHAR(50) NOT NULL,
  base_url TEXT NOT NULL,
  api_key_encrypted TEXT NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_model (
  id BIGSERIAL PRIMARY KEY,
  provider_id BIGINT NOT NULL REFERENCES ai_model_provider(id),
  model_name VARCHAR(128) NOT NULL,
  model_type VARCHAR(32) NOT NULL,
  context_window INT,
  input_price DECIMAL(12, 6),
  output_price DECIMAL(12, 6),
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_base (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  visibility VARCHAR(30) DEFAULT 'private',
  created_by BIGINT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_document (
  id BIGSERIAL PRIMARY KEY,
  kb_id BIGINT NOT NULL REFERENCES knowledge_base(id),
  filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(50),
  file_url TEXT,
  file_size BIGINT,
  parse_status VARCHAR(50) DEFAULT 'pending',
  chunk_count INT DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_chunk (
  id BIGSERIAL PRIMARY KEY,
  kb_id BIGINT NOT NULL REFERENCES knowledge_base(id),
  document_id BIGINT NOT NULL REFERENCES knowledge_document(id),
  content TEXT NOT NULL,
  chunk_index INT NOT NULL,
  token_count INT,
  embedding VECTOR(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_kb_id ON knowledge_chunk(kb_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_document_id ON knowledge_chunk(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_embedding ON knowledge_chunk USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS agent (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  system_prompt TEXT,
  model_id BIGINT REFERENCES ai_model(id),
  temperature DECIMAL(3, 2) DEFAULT 0.7,
  enabled BOOLEAN DEFAULT TRUE,
  created_by BIGINT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_tool (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  tool_type VARCHAR(50) NOT NULL,
  description TEXT,
  schema JSONB,
  config JSONB,
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS llm_call_log (
  id BIGSERIAL PRIMARY KEY,
  provider VARCHAR(100),
  model VARCHAR(100),
  scenario VARCHAR(100),
  prompt_tokens INT DEFAULT 0,
  completion_tokens INT DEFAULT 0,
  total_tokens INT DEFAULT 0,
  cost DECIMAL(12, 6) DEFAULT 0,
  latency_ms INT,
  status VARCHAR(50),
  error_message TEXT,
  created_by BIGINT,
  created_at TIMESTAMP DEFAULT NOW()
);
