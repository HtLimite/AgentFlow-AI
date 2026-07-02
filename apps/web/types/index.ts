export type DashboardMetric = {
  label: string;
  value: string;
  change: string;
};

export type KnowledgeDocumentStatus = "pending" | "parsing" | "parsed" | "embedding" | "ready" | "failed";

export type WorkflowNodeType = "start" | "llm" | "knowledge" | "condition" | "http" | "end";
