import { Code2, FileCode, FileText, Database, Inbox } from "lucide-react";
import { useOrchestration } from "@/context/orchestration-context";
import { cn } from "@/lib/utils";
import type { Artifact } from "@/types/orchestration";

const kindIcon = {
  code: FileCode,
  file: FileText,
  data: Database,
  markdown: FileText,
} as const;

function ArtifactView({ artifact }: { artifact: Artifact }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <div className="flex min-w-0 items-center gap-2">
          <Code2 className="h-4 w-4 shrink-0 text-primary" />
          <span className="truncate font-mono text-xs">{artifact.title}</span>
        </div>
        <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
          {artifact.language ?? artifact.kind}
        </span>
      </div>
      <pre className="flex-1 overflow-auto bg-surface p-4 text-[12px] leading-relaxed text-foreground/90">
        <code>{artifact.content}</code>
      </pre>
    </div>
  );
}

export function ArtifactsPanel() {
  const { artifacts, selectedArtifactId, selectArtifact } = useOrchestration();
  const current = artifacts.find((a) => a.id === selectedArtifactId) ?? artifacts[artifacts.length - 1];

  return (
    <aside className="flex h-full w-[420px] shrink-0 flex-col border-l border-border bg-sidebar">
      <header className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold tracking-tight">Canvas</h2>
          <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
            {artifacts.length} artifact{artifacts.length === 1 ? "" : "s"}
          </span>
        </div>
        <p className="mt-0.5 text-[11px] text-muted-foreground">Generated outputs from agents</p>
      </header>

      {artifacts.length > 0 && (
        <div className="flex gap-1 overflow-x-auto border-b border-border px-2 py-2">
          {artifacts.map((a) => {
            const Icon = kindIcon[a.kind];
            const active = current?.id === a.id;
            return (
              <button
                key={a.id}
                onClick={() => selectArtifact(a.id)}
                className={cn(
                  "inline-flex shrink-0 items-center gap-1.5 rounded-md border px-2 py-1 font-mono text-[11px] transition-colors",
                  active
                    ? "border-primary/50 bg-primary/10 text-foreground"
                    : "border-border bg-surface text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon className="h-3 w-3" />
                {a.title}
              </button>
            );
          })}
        </div>
      )}

      <div className="flex-1 overflow-hidden">
        {current ? (
          <ArtifactView artifact={current} />
        ) : (
          <div className="flex h-full flex-col items-center justify-center px-6 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full border border-dashed border-border">
              <Inbox className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="mt-3 text-sm font-medium">No artifacts yet</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Files, code, and structured data produced by your agents will appear here in real time.
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}