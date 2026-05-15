import type { StreamEvent } from "@/types/orchestration";

let counter = 0;
const id = () => `evt_${Date.now()}_${counter++}`;
const ts = () => new Date().toISOString();

export const mockScript: Omit<StreamEvent, "id" | "timestamp">[] = [
  { event: "agent_start", agent_name: "Manager", data: "Decomposing task: 'Build a market report on agentic AI startups in 2026'." },
  { event: "agent_thought", agent_name: "Manager", data: "I'll dispatch the Researcher to gather sources, then route findings to the Analyst, and finally have the Coder generate a visualization." },
  { event: "agent_complete", agent_name: "Manager", data: "Plan ready. Handing off to Researcher." },

  { event: "agent_start", agent_name: "Researcher", data: "Beginning web research pass." },
  { event: "tool_start", agent_name: "Researcher", data: "Querying: 'agentic AI startup funding 2026'", tool: "google_search", tool_status: "running" },
  { event: "tool_end", agent_name: "Researcher", data: "Retrieved 14 sources, 4 high-relevance.", tool: "google_search", tool_status: "success" },
  { event: "agent_thought", agent_name: "Researcher", data: "Top sources: Crunchbase, The Information, Sequoia memo, a16z agents thesis. Cross-referencing for funding totals." },
  { event: "tool_start", agent_name: "Researcher", data: "Fetching: crunchbase.com/hub/agentic-ai", tool: "fetch_url", tool_status: "running" },
  { event: "tool_end", agent_name: "Researcher", data: "Parsed 38KB of HTML.", tool: "fetch_url", tool_status: "success" },
  { event: "artifact", agent_name: "Researcher", data: "Saved research notes.", artifact: {
      id: "art_1", title: "research-notes.md", kind: "markdown", agent: "Researcher", createdAt: new Date().toISOString(),
      content: `# Agentic AI — Market Snapshot 2026\n\n## Funding\n- Total disclosed: **$8.4B** across 142 deals\n- Median seed: $6.1M\n- 17 unicorns minted in 2026\n\n## Themes\n1. Multi-agent orchestration frameworks\n2. Browser-using agents\n3. Vertical agents (legal, ops, support)\n\n## Top deals\n- Adept follow-on — $400M\n- Cognition Series C — $300M\n- Sierra — $250M\n` } },
  { event: "agent_complete", agent_name: "Researcher", data: "Research bundle ready." },

  { event: "agent_start", agent_name: "Analyst", data: "Synthesizing structured insights from the research bundle." },
  { event: "agent_thought", agent_name: "Analyst", data: "Funding is concentrated in orchestration + vertical agents. I'll surface a 3-segment breakdown." },
  { event: "require_approval", agent_name: "Analyst", data: "I'd like to call the internal pricing API to enrich segment-level revenue estimates.", approval: { action: "Call internal API: /v1/market/pricing", risk: "medium" } },

  { event: "tool_start", agent_name: "Analyst", data: "Calling pricing API…", tool: "internal_api", tool_status: "running" },
  { event: "tool_end", agent_name: "Analyst", data: "Returned 3 segments with ARR estimates.", tool: "internal_api", tool_status: "success" },
  { event: "agent_complete", agent_name: "Analyst", data: "Analysis ready, dispatching to Coder for visualization." },

  { event: "agent_start", agent_name: "Coder", data: "Generating a React chart component for the report." },
  { event: "tool_start", agent_name: "Coder", data: "Writing file: SegmentChart.tsx", tool: "execute_code", tool_status: "running" },
  { event: "tool_end", agent_name: "Coder", data: "Compiled successfully.", tool: "execute_code", tool_status: "success" },
  { event: "artifact", agent_name: "Coder", data: "Component generated.", artifact: {
      id: "art_2", title: "SegmentChart.tsx", kind: "code", language: "tsx", agent: "Coder", createdAt: new Date().toISOString(),
      content: `import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";\n\nconst data = [\n  { segment: "Orchestration", arr: 420 },\n  { segment: "Vertical Agents", arr: 690 },\n  { segment: "Browser Agents", arr: 180 },\n];\n\nexport function SegmentChart() {\n  return (\n    <BarChart width={520} height={280} data={data}>\n      <XAxis dataKey="segment" />\n      <YAxis />\n      <Tooltip />\n      <Bar dataKey="arr" fill="#7c93ff" />\n    </BarChart>\n  );\n}\n` } },
  { event: "agent_output", agent_name: "Manager", data: "Report compiled. Three artifacts produced: research notes, segment analysis, and a chart component. Total wall time: 47.2s across 4 agents and 6 tool invocations." },
  { event: "agent_complete", agent_name: "Manager", data: "Workflow complete." },
];

export function makeEvent(template: Omit<StreamEvent, "id" | "timestamp">): StreamEvent {
  return { ...template, id: id(), timestamp: ts() };
}