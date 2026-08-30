import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';

export default function App() {
  const [logs, setLogs] = useState("Loading system logs...");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "### 🟢 SysOps Copilot Ready (Enterprise Architecture v4.0)\nConnected to **18,000+ authentic production logs** across 14 service subfolders.\n\n* **Pillar 1**: Multi-tier Storage & Sub-10ms Semantic Cache\n* **Pillar 2**: Two-Stage Hybrid Search (BM25 + FAISS via RRF) + Cross-Encoder Re-Ranking\n* **Pillar 3**: Multi-Turn Query Contextualizer\n* **Pillar 4**: Guardian Safety Protocol & Command Inspection\n* **Pillar 5**: Exponential Backoff Resilience\n* **Pillar 6**: Telemetry Observability"
    }
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [telemetry, setTelemetry] = useState({ total_queries: 0, avg_latency_ms: 0, success_rate: 100 });
  const [health, setHealth] = useState({ status: "checking", provider: "..." });
  
  const chatEndRef = useRef(null);

  const fetchData = async () => {
    try {
      const logRes = await fetch("/api/logs");
      const logData = await logRes.json();
      setLogs(logData.logs || "No logs available");

      const telemRes = await fetch("/api/telemetry");
      const telemData = await telemRes.json();
      setTelemetry(telemData);

      const healthRes = await fetch("/api/health");
      const healthData = await healthRes.json();
      setHealth(healthData);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const query = queryText || inputQuery;
    if (!query.trim() || loading) return;

    // Send recent conversation history for multi-turn query rewriting
    const historyPayload = messages.slice(-4).map(m => ({ role: m.role, content: m.content }));

    const newMessages = [...messages, { role: "user", content: query }];
    setMessages(newMessages);
    setInputQuery("");
    setLoading(true);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, chat_history: historyPayload })
      });
      const data = await res.json();
      
      setMessages([...newMessages, {
        role: "assistant",
        content: data.answer,
        latency: data.latency_ms,
        guardrail: data.guardrail_triggered,
        cache_hit: data.is_cache_hit
      }]);
      fetchData();
    } catch (err) {
      setMessages([...newMessages, {
        role: "assistant",
        content: "⚠️ **API Connection Error**: Could not reach backend server."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-[#090d16] text-slate-100">
      {/* Top Navigation Header */}
      <header className="h-16 border-b border-slate-800 glass-panel px-6 flex items-center justify-between z-10">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-500/20">
            ⚙️
          </div>
          <div>
            <h1 className="text-xl font-extrabold font-outfit bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
              SysOps Copilot Enterprise v4.0
            </h1>
            <p className="text-xs text-slate-400">Hybrid Search (BM25 + FAISS) • Re-Ranker • Semantic Cache</p>
          </div>
        </div>

        {/* Health Status Pill */}
        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1.5 flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">LLM: <strong className="text-emerald-400">{health.provider}</strong></span>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-300">
            Avg Latency: <strong className="text-blue-400">{telemetry.avg_latency_ms}ms</strong>
          </div>
        </div>
      </header>

      {/* Main Dashboard Split Screen */}
      <div className="flex-1 flex overflow-hidden p-4 gap-4">
        
        {/* Left Pane: Live Log Stream Inspector */}
        <div className="w-5/12 glass-panel rounded-2xl flex flex-col overflow-hidden border border-slate-800">
          <div className="px-4 py-3 border-b border-slate-800/80 bg-slate-900/50 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-emerald-400 font-bold text-sm">📄 Live Log Inspector</span>
              <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] px-2 py-0.5 rounded-full font-mono">
                14 Subfolders (18,000+ Lines)
              </span>
            </div>
            <button onClick={fetchData} className="text-xs text-slate-400 hover:text-emerald-400 flex items-center space-x-1 transition">
              <span>🔄 Refresh</span>
            </button>
          </div>

          {/* Terminal Log Display */}
          <div className="flex-1 p-4 font-mono text-xs bg-[#030712] overflow-y-auto leading-relaxed text-emerald-400/90">
            {logs.split('\n').map((line, idx) => {
              let color = "text-slate-300";
              if (line.includes("CRITICAL")) color = "text-red-400 bg-red-950/40 font-bold px-1 rounded";
              else if (line.includes("ERROR")) color = "text-rose-400 font-semibold";
              else if (line.includes("WARNING")) color = "text-amber-400";
              else if (line.includes("INFO")) color = "text-slate-400";
              else if (line.startsWith("===")) color = "text-emerald-400 font-bold border-b border-slate-800 my-2 pt-2";
              return <div key={idx} className={`py-0.5 ${color}`}>{line}</div>;
            })}
          </div>
        </div>

        {/* Right Pane: RAG Chat Terminal */}
        <div className="w-7/12 glass-panel rounded-2xl flex flex-col overflow-hidden border border-slate-800">
          <div className="px-4 py-3 border-b border-slate-800/80 bg-slate-900/50 flex items-center justify-between">
            <span className="text-emerald-400 font-bold text-sm">💬 Resolution Console</span>
            <span className="text-xs text-slate-400 font-mono">Guardian Protocol & Semantic Cache Active</span>
          </div>

          {/* Chat Message History */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[90%] rounded-2xl p-4 ${
                  msg.role === 'user' 
                    ? 'bg-slate-800 text-slate-100 border border-slate-700 rounded-br-none' 
                    : 'bg-[#0f172a] text-slate-200 border-l-4 border-emerald-500 border-t border-r border-b border-slate-800 rounded-bl-none shadow-lg'
                }`}>
                  {msg.cache_hit && (
                    <div className="mb-2 bg-emerald-950/80 text-emerald-300 border border-emerald-800 text-xs px-2.5 py-1 rounded-lg flex items-center space-x-1.5 font-mono">
                      <span>⚡</span>
                      <span>Sub-10ms Semantic Cache Hit</span>
                    </div>
                  )}
                  {msg.guardrail && (
                    <div className="mb-2 bg-amber-950/80 text-amber-300 border border-amber-800 text-xs px-2.5 py-1 rounded-lg flex items-center space-x-1.5 font-mono">
                      <span>🛡️</span>
                      <span>Safety Guardrail Triggered</span>
                    </div>
                  )}
                  
                  <div 
                    className="markdown-body text-sm"
                    dangerouslySetInnerHTML={{ __html: marked.parse(msg.content) }}
                  />
                  
                  {msg.latency && (
                    <div className="mt-2 text-[10px] text-slate-500 font-mono flex items-center justify-end space-x-2">
                      <span>⚡ Latency: {msg.latency.toFixed(0)}ms</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-900 text-slate-400 border border-slate-800 rounded-2xl p-4 text-xs font-mono flex items-center space-x-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
                  <span>Executing Hybrid RRF Search, Re-Ranking & Diagnosing...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Incident Buttons */}
          <div className="px-4 py-2 bg-slate-950/60 border-t border-slate-800 flex items-center gap-2 overflow-x-auto text-xs">
            <span className="text-slate-500 font-mono text-[11px]">Quick Scenarios:</span>
            <button onClick={() => handleSend("Kafka consumer group 'order-processing-group' is experiencing high consumer lag. How to fix?")} className="bg-slate-900 hover:bg-slate-800 text-emerald-400 border border-slate-800 rounded-lg px-2.5 py-1 transition font-mono text-[11px] whitespace-nowrap">
              📊 Kafka Consumer Lag
            </button>
            <button onClick={() => handleSend("Redis cluster reports 'OOM command not allowed when used memory > maxmemory'. What is the resolution?")} className="bg-slate-900 hover:bg-slate-800 text-emerald-400 border border-slate-800 rounded-lg px-2.5 py-1 transition font-mono text-[11px] whitespace-nowrap">
              ⚡ Redis OOM Eviction
            </button>
            <button onClick={() => handleSend("Postgres logs show 'ERROR: deadlock detected. Process 18402 waits for ExclusiveLock'. How to resolve?")} className="bg-slate-900 hover:bg-slate-800 text-emerald-400 border border-slate-800 rounded-lg px-2.5 py-1 transition font-mono text-[11px] whitespace-nowrap">
              🐘 Postgres Deadlock
            </button>
            <button onClick={() => handleSend("AWS S3 reports '403 Access Denied' and '503 Slow Down' on bucket production-data-bucket. What SOP to follow?")} className="bg-slate-900 hover:bg-slate-800 text-emerald-400 border border-slate-800 rounded-lg px-2.5 py-1 transition font-mono text-[11px] whitespace-nowrap">
              ☁️ AWS S3 403 / 503
            </button>
          </div>

          {/* Input Area */}
          <div className="p-3 bg-slate-950/80 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Paste error logs or ask troubleshooting questions..."
              className="flex-1 glass-input rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading}
              className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold px-5 py-2.5 rounded-xl text-sm transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
            >
              Diagnose
            </button>
          </div>
        </div>

      </div>

      {/* Bottom Telemetry Footer */}
      <footer className="h-10 border-t border-slate-800 bg-slate-950/90 px-6 flex items-center justify-between text-xs text-slate-400 font-mono">
        <div className="flex items-center space-x-6">
          <span>Total Queries: <strong className="text-slate-200">{telemetry.total_queries}</strong></span>
          <span>Success Rate: <strong className="text-emerald-400">{telemetry.success_rate}%</strong></span>
        </div>
        <div>
          <span>Architecture: <strong className="text-slate-300">Enterprise Hybrid RAG (v4.0)</strong></span>
        </div>
      </footer>

    </div>
  );
}
