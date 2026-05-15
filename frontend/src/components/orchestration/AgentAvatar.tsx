import { Brain, Code2, LineChart, Search, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const iconMap: Record<string, typeof Brain> = {
  Manager: Sparkles,
  Researcher: Search,
  Analyst: LineChart,
  Coder: Code2,
};

const tintMap: Record<string, string> = {
  Manager: "from-primary/30 to-primary/10 text-primary",
  Researcher: "from-info/30 to-info/10 text-info",
  Analyst: "from-warning/30 to-warning/10 text-warning",
  Coder: "from-success/30 to-success/10 text-success",
};

export function AgentAvatar({ name, size = "md" }: { name: string; size?: "sm" | "md" }) {
  const Icon = iconMap[name] ?? Brain;
  const tint = tintMap[name] ?? "from-muted to-muted text-muted-foreground";
  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-md border border-border/60 bg-gradient-to-br",
        tint,
        size === "sm" ? "h-7 w-7" : "h-9 w-9",
      )}
    >
      <Icon className={size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4"} />
    </div>
  );
}