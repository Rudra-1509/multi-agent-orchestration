import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AgentInfo, AgentStatus, Artifact, Session, StreamEvent } from "@/types/orchestration";

const API_BASE = "http://localhost:8000";

interface OrchestrationState {
  events: StreamEvent[];
  agents: AgentInfo[];
  artifacts: Artifact[];
  sessions: Session[];
  activeSessionId: string;
  pendingApproval: StreamEvent | null;
  isStreaming: boolean;
  hasStarted: boolean;
  userPrompt: string | null;
  start: (prompt: string) => void;
  approve: () => void;
  deny: () => void;
  restart: () => void;
  selectArtifact: (id: string | null) => void;
  selectedArtifactId: string | null;
  taskId: string | null;
  error: string | null;
}

const Ctx = createContext<OrchestrationState | null>(null);

const INITIAL_AGENTS: AgentInfo[] = [
  { name: "Supervisor", role: "Orchestrator", status: "idle" },
  { name: "Researcher", role: "Search + Knowledge", status: "idle" },
  { name: "Analyst", role: "Analysis", status: "idle" },
  { name: "Executor", role: "Code Execution", status: "idle" },
  { name: "Writer", role: "Document Generation", status: "idle" },
];

const INITIAL_SESSIONS: Session[] = [
  { id: "s_now", title: "Live Agent Session", startedAt: new Date().toISOString(), status: "idle" },
];

export function OrchestrationProvider({ children }: { children: ReactNode }) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>(INITIAL_AGENTS);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [pendingApproval, setPendingApproval] = useState<StreamEvent | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedArtifactId, setSelectedArtifactId] = useState<string | null>(null);
  const [hasStarted, setHasStarted] = useState(false);
  const [userPrompt, setUserPrompt] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const setAgentStatus = (name: string, status: AgentStatus) =>
    setAgents((prev) => prev.map((a) => (a.name === name ? { ...a, status } : a)));

  const stop = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };

  useEffect(() => {
    return stop;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const subscribeToEvents = (id: string) => {
    stop();
    const source = new EventSource(`${API_BASE}/api/stream/${id}`);
    eventSourceRef.current = source;

    source.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as Record<string, unknown>;
        const event: StreamEvent = {
          event: String(data.event || "agent_thought"),
          agent_name: String(data.agent || "System"),
          timestamp: String(data.timestamp || new Date().toISOString()),
          data: String(data.message || ""),
        };

        setEvents((prev) => [...prev, event]);

        // Update agent status based on event type
        if (data.event === "started") setAgentStatus(String(data.agent), "active");
        if (data.event === "completed") setAgentStatus(String(data.agent), "complete");
        if (data.event === "error") setAgentStatus(String(data.agent), "error");
      } catch (parseError) {
        console.error("Failed to parse SSE event", parseError);
      }
    };

    source.addEventListener("done", () => {
      setIsStreaming(false);
      source.close();
    });

    source.onerror = () => {
      setError("Connection lost while streaming task events.");
      setIsStreaming(false);
      source.close();
    };
  };

  const start = async (prompt: string) => {
    if (hasStarted) return;

    try {
      setError(null);
      setHasStarted(true);
      setUserPrompt(prompt);
      setIsStreaming(true);
      setAgentStatus("Supervisor", "active");
      setEvents([
        {
          event: "agent_thought",
          agent_name: "Supervisor",
          timestamp: new Date().toISOString(),
          data: `Starting agent orchestration for: "${prompt}"`,
        },
      ]);

      // Create the task on the backend
      const response = await fetch(`${API_BASE}/api/task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: prompt,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const payload = await response.json() as { task_id: string };
      setTaskId(payload.task_id);

      // Subscribe to live events
      subscribeToEvents(payload.task_id);
    } catch (err) {
      setError(`Task creation failed: ${err}`);
      setIsStreaming(false);
      setHasStarted(false);
    }
  };

  const approve = async () => {
    if (!pendingApproval) return;
    setAgentStatus(pendingApproval.agent_name, "active");
    setEvents((prev) => [
      ...prev,
      {
        event: "agent_thought",
        agent_name: pendingApproval.agent_name,
        timestamp: new Date().toISOString(),
        data: "Human approved. Proceeding.",
      },
    ]);
    setPendingApproval(null);
    setIsStreaming(true);
  };

  const deny = () => {
    if (!pendingApproval) return;
    setAgentStatus(pendingApproval.agent_name, "idle");
    setEvents((prev) => [
      ...prev,
      {
        event: "agent_thought",
        agent_name: pendingApproval.agent_name,
        timestamp: new Date().toISOString(),
        data: "Human denied action. Aborting operation.",
      },
    ]);
    setPendingApproval(null);
  };

  const restart = () => {
    stop();
    setEvents([]);
    setArtifacts([]);
    setAgents(INITIAL_AGENTS);
    setPendingApproval(null);
    setSelectedArtifactId(null);
    setIsStreaming(false);
    setHasStarted(false);
    setUserPrompt(null);
    setTaskId(null);
    setError(null);
  };

  const value = useMemo(
    () => ({
      events,
      agents,
      artifacts,
      sessions: INITIAL_SESSIONS,
      activeSessionId: "s_now",
      pendingApproval,
      isStreaming,
      hasStarted,
      userPrompt,
      start,
      approve,
      deny,
      restart,
      selectArtifact: setSelectedArtifactId,
      selectedArtifactId,
      taskId,
      error,
    }),
    [events, agents, artifacts, pendingApproval, isStreaming, selectedArtifactId, hasStarted, userPrompt, taskId, error],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useOrchestration() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useOrchestration must be used within OrchestrationProvider");
  return ctx;
}