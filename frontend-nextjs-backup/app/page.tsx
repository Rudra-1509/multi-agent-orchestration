"use client";

import { useEffect, useRef, useState } from "react";

type EventItem = {
  agent: string;
  event: string;
  message: string;
  timestamp: string;
};

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [query, setQuery] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState("idle");
  const [events, setEvents] = useState<EventItem[]>([]);
  const [finalResponse, setFinalResponse] = useState("");
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const subscribeToEvents = (id: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const source = new EventSource(`${API_BASE}/api/stream/${id}`);
    eventSourceRef.current = source;

    source.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as EventItem;
        setEvents((prev) => [...prev, data]);
        setStatus("running");
      } catch (parseError) {
        console.error("Failed to parse SSE event", parseError);
      }
    };

    source.addEventListener("done", () => {
      setStatus("completed");
      source.close();
      fetchResult(id);
    });

    source.onerror = () => {
      setStatus("error");
      setError("Connection lost while streaming task events.");
      source.close();
    };
  };

  const fetchResult = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/results/${id}`);
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      const payload = await res.json();
      setFinalResponse(payload.final_response ?? "No final response produced.");
    } catch (err) {
      setError(`Could not fetch result: ${err}`);
    }
  };

  const startTask = async () => {
    setError(null);
    setEvents([]);
    setFinalResponse("");
    setTaskId(null);
    setStatus("starting");

    try {
      const response = await fetch(`${API_BASE}/api/task`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          messages: [{ role: "user", content: query }],
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const payload = await response.json();
      setTaskId(payload.task_id);
      setStatus(payload.status ?? "pending");
      subscribeToEvents(payload.task_id);
    } catch (err) {
      setStatus("error");
      setError(`Task creation failed: ${err}`);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 px-6 py-10 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto max-w-4xl rounded-3xl border border-slate-200 bg-white p-8 shadow-lg dark:border-slate-800 dark:bg-slate-900">
        <h1 className="mb-4 text-3xl font-semibold">Multi-Agent Orchestration</h1>
        <p className="mb-6 text-slate-600 dark:text-slate-400">
          Start a task and watch supervisor + worker progress stream live from the backend.
        </p>

        <label className="mb-3 block text-sm font-medium">Task prompt</label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          placeholder="Describe the task you want the multi-agent system to perform."
        />

        <button
          onClick={startTask}
          disabled={!query.trim() || status === "running"}
          className="mt-4 inline-flex h-12 items-center justify-center rounded-full bg-sky-600 px-6 text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {status === "running" ? "Running task…" : "Launch Task"}
        </button>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-950">
            <h2 className="text-lg font-semibold">Live Progress</h2>
            <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">Task ID: {taskId ?? "—"}</p>
            <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">Status: {status}</p>
            <div className="space-y-3 max-h-80 overflow-auto pr-2">
              {events.length === 0 ? (
                <p className="text-sm text-slate-500">No progress events yet.</p>
              ) : (
                events.map((event, index) => (
                  <div key={`${event.timestamp}-${index}`} className="rounded-2xl border border-slate-200 bg-white p-3 text-sm shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="mb-1 flex items-center justify-between gap-3 text-slate-500 dark:text-slate-400">
                      <span>{event.agent}</span>
                      <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-slate-700 dark:text-slate-200">{event.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-950">
            <h2 className="text-lg font-semibold">Final Response</h2>
            {finalResponse ? (
              <div className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-200">
                {finalResponse}
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">Final response will appear once task aggregation is complete.</p>
            )}
          </div>
        </div>

        {error ? (
          <div className="mt-6 rounded-3xl border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
            {error}
          </div>
        ) : null}
      </div>
    </div>
  );
}
