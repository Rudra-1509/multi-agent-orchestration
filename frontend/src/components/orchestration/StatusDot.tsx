import { cn } from "@/lib/utils";
import type { AgentStatus } from "@/types/orchestration";

const styles: Record<AgentStatus, string> = {
  active: "bg-success shadow-[0_0_10px_var(--success)] animate-pulse",
  idle: "bg-muted-foreground/40",
  waiting: "bg-warning shadow-[0_0_10px_var(--warning)] animate-pulse",
  complete: "bg-info",
  error: "bg-destructive",
};

export function StatusDot({ status, className }: { status: AgentStatus; className?: string }) {
  return <span className={cn("inline-block h-2 w-2 rounded-full", styles[status], className)} />;
}

export function StatusLabel({ status }: { status: AgentStatus }) {
  const map: Record<AgentStatus, string> = {
    active: "Active",
    idle: "Idle",
    waiting: "Awaiting approval",
    complete: "Complete",
    error: "Error",
  };
  return <span className="text-xs text-muted-foreground">{map[status]}</span>;
}