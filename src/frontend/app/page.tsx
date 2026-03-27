"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

// ── Types ──────────────────────────────────────────────────────────────────

interface HealthStatus {
  status: string;
  ollama_status: string;
  model_loaded: boolean;
  agents: Record<string, string>;
  budget: { ceiling: number; consumed: number; remaining: number };
  uptime_ms: number;
  version: string;
}

interface TraceResult {
  trace_id: string;
  query: string;
  status: string;
  total_latency_ms: number | null;
  retry_count: number;
  confidence_score: number | null;
  metric_breakdown: Record<string, number> | null;
  final_response: string;
  model_used?: string;
  suggestion?: string;
}

interface PipelineEvent {
  event: string;
  data: Record<string, unknown>;
  timestamp: number;
}

// ── API helpers ────────────────────────────────────────────────────────────

const API = "/api";

async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API}/health`);
  return res.json();
}

async function submitQuery(query: string): Promise<{ trace_id: string }> {
  const res = await fetch(`${API}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return res.json();
}

async function fetchTrace(traceId: string): Promise<TraceResult> {
  const res = await fetch(`${API}/traces/${traceId}`);
  return res.json();
}

// ── Confidence gauge colors ────────────────────────────────────────────────

function scoreColor(score: number): string {
  if (score >= 0.8) return "#22c55e";
  if (score >= 0.6) return "#f59e0b";
  return "#ef4444";
}

function statusLabel(status: string): { text: string; color: string } {
  switch (status) {
    case "VALIDATED":
      return { text: "Passed", color: "text-green-400" };
    case "CIRCUIT_BREAK":
      return { text: "Fallback", color: "text-red-400" };
    case "STUB":
      return { text: "Stub", color: "text-blue-400" };
    case "CORRECTED":
      return { text: "Corrected", color: "text-yellow-400" };
    default:
      return { text: status, color: "text-gray-400" };
  }
}

// ── Components ─────────────────────────────────────────────────────────────

function HealthBadge({
  label,
  ok,
}: {
  label: string;
  ok: boolean;
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span
        className={`inline-block w-2 h-2 rounded-full ${ok ? "bg-green-500 animate-pulse-dot" : "bg-red-500"}`}
      />
      <span className="text-[var(--muted)]">{label}</span>
      <span className={ok ? "text-green-400" : "text-red-400"}>
        {ok ? "Online" : "Offline"}
      </span>
    </div>
  );
}

function ConfidenceGauge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const data = [{ value: pct, fill: scoreColor(score) }];

  return (
    <div className="relative w-36 h-36">
      <ResponsiveContainer>
        <RadialBarChart
          innerRadius="75%"
          outerRadius="100%"
          data={data}
          startAngle={210}
          endAngle={-30}
          barSize={10}
        >
          <RadialBar
            dataKey="value"
            background={{ fill: "#262626" }}
            cornerRadius={5}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold" style={{ color: scoreColor(score) }}>
          {pct}%
        </span>
        <span className="text-xs text-[var(--muted)]">confidence</span>
      </div>
    </div>
  );
}

function MetricBreakdown({
  metrics,
}: {
  metrics: Record<string, number>;
}) {
  const data = Object.entries(metrics).map(([name, value]) => ({
    name: name.replace(/_/g, " "),
    value: Math.round(value * 100),
  }));

  const colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#f59e0b", "#22c55e"];

  return (
    <div className="w-full h-48">
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 20 }}>
          <XAxis type="number" domain={[0, 100]} tick={{ fill: "#737373", fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: "#a3a3a3", fontSize: 12 }}
            width={75}
          />
          <Tooltip
            contentStyle={{
              background: "#141414",
              border: "1px solid #262626",
              borderRadius: 8,
              color: "#ededed",
            }}
            formatter={(v: number) => [`${v}%`, "Score"]}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={16}>
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function EventLog({ events }: { events: PipelineEvent[] }) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  return (
    <div className="event-log max-h-56 overflow-y-auto space-y-1 font-mono text-xs">
      {events.map((e, i) => (
        <div key={i} className="flex gap-2 py-1 px-2 rounded hover:bg-white/5">
          <span
            className={`shrink-0 w-20 text-right ${
              e.event === "complete"
                ? "text-green-400"
                : e.event === "error"
                  ? "text-red-400"
                  : "text-blue-400"
            }`}
          >
            {e.event}
          </span>
          <span className="text-[var(--muted)] truncate">
            {typeof e.data === "object"
              ? JSON.stringify(e.data).slice(0, 120)
              : String(e.data)}
          </span>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [result, setResult] = useState<TraceResult | null>(null);
  const [history, setHistory] = useState<TraceResult[]>([]);
  const [expandedTrace, setExpandedTrace] = useState<string | null>(null);

  // Poll health every 10s
  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => {});
    const id = setInterval(() => {
      fetchHealth().then(setHealth).catch(() => {});
    }, 10000);
    return () => clearInterval(id);
  }, []);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!query.trim() || loading) return;

      setLoading(true);
      setEvents([]);
      setResult(null);

      try {
        const { trace_id } = await submitQuery(query.trim());

        // Connect to SSE stream
        const evtSource = new EventSource(`${API}/stream/${trace_id}`);

        evtSource.addEventListener("agent_update", (msg) => {
          const data = JSON.parse(msg.data);
          setEvents((prev) => [
            ...prev,
            { event: "agent_update", data, timestamp: Date.now() },
          ]);
        });

        evtSource.addEventListener("complete", async (msg) => {
          const data = JSON.parse(msg.data);
          setEvents((prev) => [
            ...prev,
            { event: "complete", data, timestamp: Date.now() },
          ]);
          evtSource.close();

          // Fetch full trace
          const trace = await fetchTrace(trace_id);
          setResult(trace);
          setHistory((prev) => [trace, ...prev].slice(0, 20));
          setLoading(false);
        });

        evtSource.addEventListener("error", (msg) => {
          let data = {};
          try {
            if (msg instanceof MessageEvent) data = JSON.parse(msg.data);
          } catch {
            /* ignore */
          }
          setEvents((prev) => [
            ...prev,
            { event: "error", data: data as Record<string, unknown>, timestamp: Date.now() },
          ]);
          evtSource.close();
          setLoading(false);
        });

        evtSource.onerror = () => {
          evtSource.close();
          setLoading(false);
        };
      } catch {
        setLoading(false);
      }
    },
    [query, loading]
  );

  return (
    <main className="min-h-screen p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Hallucination Guardrail
          </h1>
          <p className="text-sm text-[var(--muted)]">
            Real-time LLM response validation pipeline
          </p>
        </div>
        <div className="flex items-center gap-6">
          {health && (
            <>
              <HealthBadge label="Ollama" ok={health.ollama_status === "connected"} />
              <HealthBadge label="DeepSeek-R1" ok={health.model_loaded} />
              <HealthBadge label="Pipeline" ok={health.status === "healthy"} />
            </>
          )}
          <span className="text-xs text-[var(--muted)] border border-[var(--card-border)] rounded px-2 py-1">
            v{health?.version ?? "0.1.0"}
          </span>
        </div>
      </header>

      {/* Query Input */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question to test the guardrail pipeline..."
          className="flex-1 bg-[var(--card)] border border-[var(--card-border)] rounded-lg px-4 py-3 text-sm placeholder:text-[var(--muted)] focus:outline-none focus:border-[var(--accent)] transition-colors"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-[var(--accent)] hover:bg-[var(--accent-hover)] disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Processing
            </span>
          ) : (
            "Submit Query"
          )}
        </button>
      </form>

      {/* Pipeline Events + Result */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Event Stream - 2 cols */}
        <div className="lg:col-span-2 bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)]">
              Pipeline Events
            </h2>
            {loading && (
              <span className="flex items-center gap-1.5 text-xs text-blue-400">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse-dot" />
                Streaming
              </span>
            )}
          </div>
          {events.length === 0 && !loading ? (
            <p className="text-sm text-[var(--muted)] py-8 text-center">
              Submit a query to see real-time pipeline events
            </p>
          ) : (
            <EventLog events={events} />
          )}
        </div>

        {/* Confidence Score - 1 col */}
        <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 flex flex-col items-center justify-center space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)]">
            Confidence Score
          </h2>
          {result && result.confidence_score != null ? (
            <AnimatePresence>
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <ConfidenceGauge score={result.confidence_score} />
              </motion.div>
            </AnimatePresence>
          ) : (
            <div className="w-36 h-36 flex items-center justify-center">
              <span className="text-[var(--muted)] text-sm">--</span>
            </div>
          )}
          {result && (
            <div className="text-center space-y-1">
              <span
                className={`text-sm font-medium ${statusLabel(result.status).color}`}
              >
                {statusLabel(result.status).text}
              </span>
              <div className="flex items-center gap-3 text-xs text-[var(--muted)]">
                {result.total_latency_ms != null && (
                  <span>{Math.round(result.total_latency_ms)}ms</span>
                )}
                <span>
                  {result.retry_count} {result.retry_count === 1 ? "retry" : "retries"}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Result Panel */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Response */}
            <div className="lg:col-span-2 bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 space-y-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)]">
                Guardrailed Response
              </h2>
              {result.status === "STUB" && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs">
                  <span>&#9432;</span>
                  <span>Ollama is offline — this is a development stub, not a validated response.</span>
                </div>
              )}
              {result.final_response ? (
                <div className="markdown-response text-sm leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.final_response}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm leading-relaxed">No response generated.</p>
              )}
            </div>

            {/* Metric Breakdown */}
            <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 space-y-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)]">
                Metric Breakdown
              </h2>
              {result.metric_breakdown &&
              Object.keys(result.metric_breakdown).length > 0 ? (
                <MetricBreakdown metrics={result.metric_breakdown} />
              ) : (
                <p className="text-sm text-[var(--muted)] py-4 text-center">
                  No metrics available
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Query History */}
      {history.length > 0 && (
        <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)]">
            Query History
          </h2>
          <div className="divide-y divide-[var(--card-border)]">
            {history.map((trace) => {
              const st = statusLabel(trace.status);
              const isExpanded = expandedTrace === trace.trace_id;
              return (
                <div key={trace.trace_id}>
                  <div
                    onClick={() =>
                      setExpandedTrace((prev) =>
                        prev === trace.trace_id ? null : trace.trace_id
                      )
                    }
                    className="flex items-center justify-between py-3 first:pt-0 last:pb-0 cursor-pointer hover:bg-white/5 rounded transition-colors"
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0 mr-4">
                      <span
                        className="text-[var(--muted)] text-xs shrink-0 transition-transform duration-200"
                        style={{ transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)" }}
                      >
                        ▶
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm truncate">{trace.query}</p>
                        <p className="text-xs text-[var(--muted)] mt-0.5 font-mono">
                          {trace.trace_id.slice(0, 8)}...
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 shrink-0 text-xs">
                      <span className={st.color}>{st.text}</span>
                      {trace.confidence_score != null && (
                        <span
                          className="font-medium"
                          style={{ color: scoreColor(trace.confidence_score) }}
                        >
                          {Math.round(trace.confidence_score * 100)}%
                        </span>
                      )}
                      {trace.total_latency_ms != null && (
                        <span className="text-[var(--muted)]">
                          {Math.round(trace.total_latency_ms)}ms
                        </span>
                      )}
                      <span className="text-[var(--muted)]">
                        {trace.retry_count}x
                      </span>
                    </div>
                  </div>
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="markdown-response text-sm leading-relaxed pt-3 pb-1 px-2 border-t border-[var(--card-border)]">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {trace.final_response || "No response generated."}
                          </ReactMarkdown>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </main>
  );
}
