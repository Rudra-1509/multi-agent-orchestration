import { Activity, Plus, History } from "lucide-react";
import { useOrchestration } from "@/context/orchestration-context";
import { AgentAvatar } from "./AgentAvatar";
import { StatusDot, StatusLabel } from "./StatusDot";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const { sessions, activeSessionId, agents, restart } = useOrchestration();

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-border bg-sidebar">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-primary to-primary/40">
            <Activity className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="text-sm font-semibold tracking-tight">Orchestra</span>
        </div>
        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={restart} title="New session">
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      <div className="px-4 pt-4 pb-2">
        <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground">Agents</p>
      </div>
      <div className="flex flex-col gap-1 px-2">
        {agents.map((a) => (
          <div key={a.name} className="flex items-center gap-3 rounded-md px-2 py-2 hover:bg-accent/40">
            <AgentAvatar name={a.name} size="sm" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{a.name}</span>
                <StatusDot status={a.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-muted-foreground">{a.role}</span>
                <StatusLabel status={a.status} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex items-center gap-2 px-4 pb-2">
        <History className="h-3.5 w-3.5 text-muted-foreground" />
        <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground">History</p>
      </div>
      <div className="flex flex-1 flex-col gap-1 overflow-y-auto px-2 pb-4">
        {sessions.map((s) => (
          <button
            key={s.id}
            className={cn(
              "group flex flex-col gap-1 rounded-md px-2 py-2 text-left transition-colors hover:bg-accent/40",
              s.id === activeSessionId && "bg-accent/60",
            )}
          >
            <div className="flex items-center gap-2">
              <StatusDot status={s.status === "running" ? "active" : "complete"} />
              <span className="truncate text-sm">{s.title}</span>
            </div>
            <span className="pl-4 text-[11px] text-muted-foreground">
              {new Date(s.startedAt).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}