import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, FileText, MessageSquare, Sparkles } from "lucide-react";
import { useOrchestration } from "@/context/orchestration-context";
import type { StreamEvent } from "@/types/orchestration";
import { AgentAvatar } from "./AgentAvatar";
import { ToolBadge } from "./ToolBadge";
import { ApprovalPanel } from "./ApprovalPanel";
import { ChatInput } from "./ChatInput";
import { cn } from "@/lib/utils";

interface Group {
  agent: string;
  events: StreamEvent[];
  startedAt: string;
}

function groupEvents(events: StreamEvent[]): Group[] {
  const groups: Group[] = [];
  for (const e of events) {
    const last = groups[groups.length - 1];
    if (last && last.agent === e.agent_name) last.events.push(e);
    else groups.push({ agent: e.agent_name, events: [e], startedAt: e.timestamp });
  }
  return groups;
}

function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: "UTC",
  });
}

function StepCard({ group, index }: { group: Group; index: number }) {
  const [open, setOpen] = useState(true);
  const thoughts = group.events.filter((e) => e.event === "agent_thought");
  const tools = group.events.filter((e) => e.event === "tool_start" || e.event === "tool_end");
  const outputs = group.events.filter((e) => e.event === "agent_output");
  const isComplete = group.events.some((e) => e.event === "agent_complete");

  return (
    <div className="relative pl-10">
      <div className="absolute left-3 top-3 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-background text-[11px] font-mono text-muted-foreground">
        {index + 1}
      </div>
      <div className="absolute left-[1.45rem] top-9 bottom-[-1rem] w-px bg-border/60" />

      <div className="rounded-lg border border-border bg-card">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex w-full items-center gap-3 rounded-t-lg px-3 py-2.5 text-left hover:bg-accent/30"
        >
          <AgentAvatar name={group.agent} size="sm" />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">{group.agent}</span>
              <span className={cn("text-[10px] font-mono uppercase tracking-wider", isComplete ? "text-success" : "text-info")}>
                {isComplete ? "complete" : "running"}
              </span>
            </div>
            <span className="text-[11px] text-muted-foreground">{fmtTime(group.startedAt)} · {group.events.length} events</span>
          </div>
          <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform", !open && "-rotate-90")} />
        </button>

        {open && (
          <div className="space-y-3 border-t border-border/60 px-4 py-3">
            {thoughts.length > 0 && (
              <div>
                <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
                  <Sparkles className="h-3 w-3" /> Scratchpad
                </div>
                <div className="space-y-1.5 rounded-md border border-dashed border-border/60 bg-surface px-3 py-2">
                  {thoughts.map((t) => (
                    <p key={t.id} className="text-xs leading-relaxed text-muted-foreground">
                      <span className="text-foreground/70">›</span> {t.data}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {tools.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tools.map((t) => (
                  <ToolBadge
                    key={t.id}
                    tool={t.tool ?? "tool"}
                    status={t.tool_status ?? "running"}
                    detail={t.data}
                  />
                ))}
              </div>
            )}

            {group.events.some((e) => e.event === "artifact") && (
              <div className="flex flex-wrap gap-2">
                {group.events
                  .filter((e) => e.event === "artifact" && e.artifact)
                  .map((e) => (
                    <div key={e.id} className="inline-flex items-center gap-2 rounded-md border border-primary/30 bg-primary/5 px-2.5 py-1.5 text-xs">
                      <FileText className="h-3.5 w-3.5 text-primary" />
                      <span className="font-mono text-foreground/90">{e.artifact!.title}</span>
                      <span className="text-muted-foreground">→ Canvas</span>
                    </div>
                  ))}
              </div>
            )}

            {outputs.length > 0 && (
              <div className="space-y-2 border-t border-border/60 pt-3">
                <div className="flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
                  <MessageSquare className="h-3 w-3" /> Output
                </div>
                {outputs.map((o) => (
                  <p key={o.id} className="text-sm leading-relaxed text-foreground/90">{o.data}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StreamingBubble() {
  const { events, isStreaming } = useOrchestration();
  const last = events[events.length - 1];
  if (!last || !isStreaming) return null;
  return (
    <div className="sticky bottom-0 -mx-6 mt-4 border-t border-border/60 bg-background/80 px-6 py-3 backdrop-blur">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <span className="inline-flex h-1.5 w-1.5 animate-pulse rounded-full bg-success" />
        <span className="font-mono uppercase tracking-wider">{last.agent_name}</span>
        <span>·</span>
        <span className="truncate">{last.data}</span>
        <span className="ml-1 inline-block h-3 w-1.5 animate-pulse bg-foreground/60" />
      </div>
    </div>
  );
}

export function AgentTimeline() {
  const { events, pendingApproval, isStreaming, hasStarted, userPrompt } = useOrchestration();
  const groups = useMemo(() => groupEvents(events), [events]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [events.length]);

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <div>
          <h1 className="text-sm font-semibold tracking-tight">
            {userPrompt ?? "New session"}
          </h1>
          <p className="text-[11px] text-muted-foreground">
            Session s_now · {events.length} events · {isStreaming ? "streaming" : pendingApproval ? "paused" : "idle"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn("inline-flex h-2 w-2 rounded-full", isStreaming ? "bg-success animate-pulse" : "bg-muted-foreground/40")} />
          <span className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
            {isStreaming ? "Live" : pendingApproval ? "HIL" : "Idle"}
          </span>
        </div>
      </header>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6">
        {!hasStarted ? (
          <EmptyState />
        ) : (
          <>
            {userPrompt && (
              <div className="mb-6 flex justify-end">
                <div className="max-w-[80%] rounded-lg bg-primary px-4 py-2.5 text-sm text-primary-foreground shadow-[0_0_24px_-12px_var(--primary)]">
                  {userPrompt}
                </div>
              </div>
            )}
            <div className="space-y-4">
              {groups.map((g, i) => (
                <StepCard key={i} group={g} index={i} />
              ))}
            </div>
            {pendingApproval && (
              <div className="mt-4 pl-10">
                <ApprovalPanel />
              </div>
            )}
            <StreamingBubble />
          </>
        )}
      </div>
      <ChatInput />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="mx-auto flex h-full max-w-xl flex-col items-center justify-center text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-card">
        <Sparkles className="h-5 w-5 text-primary" />
      </div>
      <h2 className="text-lg font-semibold tracking-tight">Brief the supervisor</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Describe a task below. The supervisor will decompose it and dispatch
        Researcher, Analyst, and Coder agents — streaming their thoughts, tool
        calls, and artifacts here in real time.
      </p>
    </div>
  );
}