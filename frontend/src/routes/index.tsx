import { createFileRoute } from "@tanstack/react-router";
import { OrchestrationProvider } from "@/context/orchestration-context";
import { Sidebar } from "@/components/orchestration/Sidebar";
import { AgentTimeline } from "@/components/orchestration/AgentTimeline";
import { ArtifactsPanel } from "@/components/orchestration/ArtifactsPanel";

export const Route = createFileRoute("/")({
  component: Index,
  errorComponent: IndexError,
  head: () => ({
    meta: [
      { title: "Orchestra — Multi-Agent Control Room" },
      { name: "description", content: "Live visualization of multi-agent orchestration: timelines, tool calls, artifacts, and human-in-the-loop approvals." },
    ],
  }),
});

function IndexError() {
  return (
    <div className="flex h-screen items-center justify-center bg-background text-foreground">
      <div className="rounded border p-6 text-center">
        <h1 className="text-lg font-semibold">Something went wrong</h1>
        <p className="text-sm text-muted-foreground">Please refresh the page and try again.</p>
      </div>
    </div>
  );
}

function Index() {
  return (
    <OrchestrationProvider>
      <div className="flex h-screen w-full overflow-hidden bg-background text-foreground">
        <Sidebar />
        <main className="flex min-w-0 flex-1">
          <AgentTimeline />
          <ArtifactsPanel />
        </main>
      </div>
    </OrchestrationProvider>
  );
}
