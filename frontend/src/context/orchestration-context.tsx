import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AgentInfo, AgentStatus, Artifact, EventType, Session, StreamEvent } from "@/types/orchestration";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const EVENT_TYPES: EventType[] = ["agent_start", "agent_thought", "tool_start", "tool_end", "agent_output", "require_approval", "artifact", "agent_complete"];

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
  { id: "s_now", title: "Live Agent Session", startedAt: "1970-01-01T00:00:00.000Z", status: "idle" },
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
        const eventType: EventType = EVENT_TYPES.includes(data.event as EventType) ? (data.event as EventType) : "agent_thought";
        const event: StreamEvent = {
          id: crypto.randomUUID(),
          event: eventType,
          agent_name: typeof data.agent === "string" ? data.agent : "System",
          timestamp: typeof data.timestamp === "string" ? data.timestamp : new Date().toISOString(),
          data: typeof data.message === "string" ? data.message : "",
        };

        setEvents((prev) => [...prev, event]);

        // Update agent status based on event type
        if (data.event === "started") setAgentStatus(typeof data.agent === "string" ? data.agent : "Supervisor", "active");
        if (data.event === "completed") setAgentStatus(typeof data.agent === "string" ? data.agent : "Supervisor", "complete");
        if (data.event === "error") setAgentStatus(typeof data.agent === "string" ? data.agent : "Supervisor", "error");
      } catch (parseError) {
        console.error("Failed to parse SSE event", parseError);
      }
    };

    source.addEventListener("done", () => {
      setIsStreaming(false);
      source.close();
      if (eventSourceRef.current === source) {
        eventSourceRef.current = null;
      }
    });

    source.onerror = () => {
      setError("Connection lost while streaming task events.");
      setIsStreaming(false);
      source.close();
      if (eventSourceRef.current === source) {
        eventSourceRef.current = null;
      }
    };
  };

  const createTaskWithRetry = async (prompt: string, retries = 3): Promise<{ task_id: string }> => {
    let attempt = 0;
    let lastError: unknown = null;
    while (attempt < retries) {
      try {
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
        return await response.json() as { task_id: string };
      } catch (err) {
        lastError = err;
        attempt += 1;
        if (attempt < retries) {
          await new Promise((resolve) => setTimeout(resolve, 300 * 2 ** attempt));
        }
      }
    }
    throw lastError ?? new Error("Task creation failed");
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
          id: crypto.randomUUID(),
          event: "agent_thought",
          agent_name: "Supervisor",
          timestamp: new Date().toISOString(),
          data: `Starting agent orchestration for: "${prompt}"`,
        },
      ]);

      const payload = await createTaskWithRetry(prompt);
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
        id: crypto.randomUUID(),
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
        id: crypto.randomUUID(),
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
