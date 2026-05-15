import { useState, type FormEvent, type KeyboardEvent } from "react";
import { ArrowUp, RotateCcw, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useOrchestration } from "@/context/orchestration-context";
import { cn } from "@/lib/utils";

const SUGGESTIONS = [
  "Build a market report on agentic AI startups in 2026",
  "Refactor the billing service for multi-tenant support",
  "Investigate Q2 churn and propose interventions",
];

export function ChatInput() {
  const { start, restart, hasStarted, isStreaming, pendingApproval } = useOrchestration();
  const [value, setValue] = useState("");

  const submit = (e?: FormEvent) => {
    e?.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || hasStarted) return;
    start(trimmed);
    setValue("");
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const status = pendingApproval
    ? "Awaiting human approval"
    : isStreaming
      ? "Supervisor is orchestrating agents…"
      : hasStarted
        ? "Run complete"
        : "Ready";

  return (
    <div className="border-t border-border bg-background/95 px-6 py-4 backdrop-blur">
      <div className="mx-auto max-w-3xl">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
            <span
              className={cn(
                "inline-flex h-1.5 w-1.5 rounded-full",
                isStreaming ? "bg-success animate-pulse" : pendingApproval ? "bg-warning" : "bg-muted-foreground/40",
              )}
            />
            <span className="font-mono uppercase tracking-widest">{status}</span>
          </div>
          {hasStarted && (
            <button
              onClick={restart}
              className="inline-flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-widest text-muted-foreground transition-colors hover:text-foreground"
            >
              <RotateCcw className="h-3 w-3" /> New run
            </button>
          )}
        </div>

        <form
          onSubmit={submit}
          className={cn(
            "group relative rounded-xl border bg-card transition-colors",
            hasStarted ? "border-border/40 opacity-60" : "border-border focus-within:border-primary/60 focus-within:shadow-[0_0_24px_-12px_var(--primary)]",
          )}
        >
          <Textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={hasStarted}
            placeholder={
              hasStarted
                ? "Run in progress — start a new run to send another task."
                : "Describe a task for the supervisor to orchestrate…"
            }
            className="min-h-[64px] resize-none border-0 bg-transparent px-4 pb-12 pt-3 text-sm shadow-none focus-visible:ring-0"
          />
          <div className="absolute bottom-2 left-3 flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
            <Sparkles className="h-3 w-3" />
            Supervisor → Researcher → Analyst → Coder
          </div>
          <Button
            type="submit"
            size="icon"
            disabled={!value.trim() || hasStarted}
            className="absolute bottom-2 right-2 h-8 w-8 rounded-lg"
          >
            <ArrowUp className="h-4 w-4" />
          </Button>
        </form>

        {!hasStarted && (
          <div className="mt-3 flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setValue(s)}
                className="rounded-full border border-border bg-card px-3 py-1 text-[11px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}