import { AlertTriangle, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useOrchestration } from "@/context/orchestration-context";
import { AgentAvatar } from "./AgentAvatar";

export function ApprovalPanel() {
  const { pendingApproval, approve, deny } = useOrchestration();
  if (!pendingApproval) return null;
  const risk = pendingApproval.approval?.risk ?? "medium";
  const riskColor =
    risk === "high" ? "text-destructive" : risk === "medium" ? "text-warning" : "text-info";

  return (
    <div className="rounded-lg border border-warning/40 bg-warning/5 p-4 shadow-[0_0_24px_-8px_var(--warning)]">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-md bg-warning/15">
          <AlertTriangle className="h-4 w-4 text-warning" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-foreground">Human approval required</span>
            <span className={`text-xs font-mono uppercase ${riskColor}`}>· {risk} risk</span>
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
            <AgentAvatar name={pendingApproval.agent_name} size="sm" />
            <span className="font-medium text-foreground">{pendingApproval.agent_name}</span>
            <span>wants to:</span>
          </div>
          <p className="mt-1.5 rounded-md border border-border/60 bg-surface px-3 py-2 font-mono text-xs text-foreground/90">
            {pendingApproval.approval?.action}
          </p>
          <p className="mt-2 text-sm text-muted-foreground">{pendingApproval.data}</p>
          <div className="mt-4 flex gap-2">
            <Button size="sm" onClick={approve} className="bg-success text-background hover:bg-success/90">
              <Check className="h-4 w-4" /> Approve
            </Button>
            <Button size="sm" variant="outline" onClick={deny}>
              <X className="h-4 w-4" /> Deny &amp; fallback
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}