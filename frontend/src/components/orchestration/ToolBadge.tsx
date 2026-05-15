import { Check, Loader2, Wrench, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  tool: string;
  status: "running" | "success" | "error";
  detail?: string;
}

export function ToolBadge({ tool, status, detail }: Props) {
  const Icon = status === "running" ? Loader2 : status === "success" ? Check : X;
  return (
    <div
      className={cn(
        "inline-flex items-start gap-2 rounded-md border bg-surface-elevated px-2.5 py-1.5 text-xs font-mono",
        status === "running" && "border-info/40 text-info",
        status === "success" && "border-success/30 text-success",
        status === "error" && "border-destructive/40 text-destructive",
      )}
    >
      <Wrench className="mt-0.5 h-3.5 w-3.5 opacity-70" />
      <span className="text-foreground/90">[{tool}]</span>
      <Icon className={cn("mt-0.5 h-3.5 w-3.5", status === "running" && "animate-spin")} />
      {detail && <span className="text-muted-foreground font-sans">{detail}</span>}
    </div>
  );
}