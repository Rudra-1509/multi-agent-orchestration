export type AgentStatus = "active" | "idle" | "waiting" | "complete" | "error";

export type EventType =
  | "agent_start"
  | "agent_thought"
  | "tool_start"
  | "tool_end"
  | "agent_output"
  | "require_approval"
  | "artifact"
  | "agent_complete";

export interface StreamEvent {
  id: string;
  event: EventType;
  agent_name: string;
  data: string;
  timestamp: string;
  tool?: string;
  tool_status?: "running" | "success" | "error";
  approval?: { action: string; risk: "low" | "medium" | "high" };
  artifact?: Artifact;
}

export interface Artifact {
  id: string;
  title: string;
  kind: "code" | "file" | "data" | "markdown";
  language?: string;
  content: string;
  agent: string;
  createdAt: string;
}

export interface AgentInfo {
  name: string;
  role: string;
  status: AgentStatus;
}

export interface Session {
  id: string;
  title: string;
  startedAt: string;
  status: "running" | "complete" | "paused";
}