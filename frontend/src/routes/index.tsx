import { createFileRoute } from "@tanstack/react-router";
import { OrchestrationProvider } from "@/context/orchestration-context";
import { Sidebar } from "@/components/orchestration/Sidebar";
import { AgentTimeline } from "@/components/orchestration/AgentTimeline";
import { ArtifactsPanel } from "@/components/orchestration/ArtifactsPanel";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Orchestra — Multi-Agent Control Room" },
      { name: "description", content: "Live visualization of multi-agent orchestration: timelines, tool calls, artifacts, and human-in-the-loop approvals." },
    ],
  }),
});

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
