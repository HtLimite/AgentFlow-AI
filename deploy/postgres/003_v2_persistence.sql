CREATE TABLE IF NOT EXISTS prompt_template (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  scenario VARCHAR(100) DEFAULT 'general',
  content TEXT NOT NULL,
  current_version INT DEFAULT 1,
  tenant_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prompt_version (
  id BIGSERIAL PRIMARY KEY,
  prompt_id BIGINT NOT NULL REFERENCES prompt_template(id) ON DELETE CASCADE,
  version INT NOT NULL,
  content TEXT NOT NULL,
  change_note TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_definition (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  definition_json JSONB NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  tenant_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_run (
  id BIGSERIAL PRIMARY KEY,
  workflow_id BIGINT NOT NULL,
  status VARCHAR(50) DEFAULT 'running',
  input_json JSONB,
  output_json JSONB,
  tenant_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_node_run (
  id BIGSERIAL PRIMARY KEY,
  run_id BIGINT NOT NULL REFERENCES workflow_run(id) ON DELETE CASCADE,
  node_id VARCHAR(100) NOT NULL,
  node_type VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'success',
  input_json JSONB,
  output_json JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eval_dataset (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  tenant_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eval_case (
  id BIGSERIAL PRIMARY KEY,
  dataset_id BIGINT NOT NULL REFERENCES eval_dataset(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  expected_answer TEXT,
  scoring_criteria TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eval_run (
  id BIGSERIAL PRIMARY KEY,
  dataset_id BIGINT NOT NULL,
  model VARCHAR(100) NOT NULL,
  status VARCHAR(50) DEFAULT 'completed',
  score DECIMAL(6, 2) DEFAULT 0,
  result_json JSONB,
  tenant_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tool_audit_log (
  id BIGSERIAL PRIMARY KEY,
  trace_id VARCHAR(120) NOT NULL,
  agent_id BIGINT,
  tool_name VARCHAR(100) NOT NULL,
  input_json JSONB,
  output_json JSONB,
  status VARCHAR(50) DEFAULT 'success',
  latency_ms INT DEFAULT 0,
  error_message TEXT,
  tenant_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS total_tokens INT DEFAULT 0;
ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS latency_ms INT;
ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS status VARCHAR(50);
ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS metadata_json JSONB;

CREATE INDEX IF NOT EXISTS idx_prompt_template_scenario ON prompt_template(scenario);
CREATE INDEX IF NOT EXISTS idx_workflow_run_workflow_id ON workflow_run(workflow_id);
CREATE INDEX IF NOT EXISTS idx_eval_run_dataset_id ON eval_run(dataset_id);
CREATE INDEX IF NOT EXISTS idx_llm_call_log_created_at ON llm_call_log(created_at);
CREATE INDEX IF NOT EXISTS idx_tool_audit_log_trace_id ON tool_audit_log(trace_id);
CREATE INDEX IF NOT EXISTS idx_tool_audit_log_created_at ON tool_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_tool_audit_log_tool_name ON tool_audit_log(tool_name);
