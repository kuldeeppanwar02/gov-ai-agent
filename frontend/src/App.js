import React, { useState, useRef, useEffect } from "react";
import "./App.css";

const API = "http://localhost:8000";

const PRIORITY_COLOR = { High: "#22c55e", Medium: "#f59e0b", Low: "#94a3b8" };
const CATEGORY_ICON = {
  "Agriculture": "🌾", "Health": "🏥", "Education": "📚", "Housing": "🏠",
  "Financial Inclusion": "🏦", "Women & Child": "👩‍👧", "Employment": "💼",
  "Business & Entrepreneurship": "🚀", "Energy & Utilities": "⚡",
  "Pension & Social Security": "🧓", "Insurance": "🛡️",
  "Skill Development": "🛠️", "Disability": "♿",
};

export default function App() {
  const [step, setStep] = useState(1); // 1=upload, 2=results, 3=apply
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [profile, setProfile] = useState(null);
  const [schemes, setSchemes] = useState([]);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [applyResult, setApplyResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    { role: "ai", text: "Namaste! 🙏 I'm your Gov AI assistant. Ask me anything about government schemes, eligibility, or how to apply." }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // ── Upload & Analyze ──────────────────────────
  const handleUpload = async () => {
    if (!file) { setError("Please select a document first."); return; }
    setLoading(true); setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: formData });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Upload failed"); }
      const data = await res.json();
      setProfile(data.profile);
      setSchemes(data.eligible_schemes || []);
      setStep(2);
    } catch (e) {
      setError(e.message || "Something went wrong. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // ── Auto Apply ────────────────────────────────
  const handleApply = async (scheme) => {
    setSelectedScheme(scheme);
    setStep(3);
    setApplyResult(null);
    try {
      const res = await fetch(`${API}/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scheme_name: scheme.scheme_name, profile })
      });
      const data = await res.json();
      setApplyResult(data);
    } catch {
      setApplyResult({ status: "error", message: "Could not reach backend." });
    }
  };

  // ── Chat ──────────────────────────────────────
  const handleChat = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatMessages(m => [...m, { role: "user", text: userMsg }]);
    setChatInput("");
    setChatLoading(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, profile: profile || {} })
      });
      const data = await res.json();
      setChatMessages(m => [...m, { role: "ai", text: data.reply }]);
    } catch {
      setChatMessages(m => [...m, { role: "ai", text: "Sorry, I couldn't reach the server right now. Please check if the backend is running." }]);
    } finally {
      setChatLoading(false);
    }
  };

  // ── Drag and drop ─────────────────────────────
  const handleDrop = (e) => {
    e.preventDefault(); setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) { setFile(dropped); setError(""); }
  };

  // ─────────────────────────────────────────────
  //  RENDER
  // ─────────────────────────────────────────────
  return (
    <div className="app-root">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">🇮🇳</span>
            <div>
              <span className="logo-title">Gov<span className="logo-accent">AI</span> Agent</span>
              <span className="logo-sub">Powered by Amazon Nova</span>
            </div>
          </div>
          <div className="nova-badge">
            <span className="nova-dot" />
            Amazon Nova Lite + Titan Embeddings
          </div>
        </div>
      </header>

      {/* ── Progress Steps ── */}
      <div className="steps-bar">
        {["Upload Document", "Eligible Schemes", "Apply & Chat"].map((label, i) => (
          <div key={i} className={`step-item ${step > i + 1 ? "done" : ""} ${step === i + 1 ? "active" : ""}`}>
            <div className="step-bubble">{step > i + 1 ? "✓" : i + 1}</div>
            <span>{label}</span>
            {i < 2 && <div className="step-line" />}
          </div>
        ))}
      </div>

      <main className="main-content">
        {/* ════════════════════════════════════════
            STEP 1 — Upload
        ════════════════════════════════════════ */}
        {step === 1 && (
          <div className="card upload-card">
            <h1 className="card-title">Find Your Government Benefits</h1>
            <p className="card-subtitle">
              Upload any document mentioning your age, income, location, or occupation —
              Nova AI will extract your profile and find all eligible schemes.
            </p>

            <div
              className={`dropzone ${dragOver ? "drag-active" : ""} ${file ? "has-file" : ""}`}
              onClick={() => fileInputRef.current.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              <input ref={fileInputRef} type="file" accept=".txt,.pdf,.doc,.docx"
                onChange={(e) => { setFile(e.target.files[0]); setError(""); }} hidden />
              {file ? (
                <>
                  <div className="file-icon">📄</div>
                  <div className="file-name">{file.name}</div>
                  <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
                  <button className="btn-secondary small" onClick={(e) => { e.stopPropagation(); setFile(null); }}>Remove</button>
                </>
              ) : (
                <>
                  <div className="drop-icon">☁️</div>
                  <div className="drop-label">Drag & drop or click to upload</div>
                  <div className="drop-hint">Supports .txt · .pdf · .doc · .docx</div>
                </>
              )}
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}

            <button className={`btn-primary ${!file || loading ? "disabled" : ""}`}
              onClick={handleUpload} disabled={!file || loading}>
              {loading ? <><span className="spinner" /> Analyzing with Nova AI...</> : "🔍 Analyze & Find Schemes"}
            </button>

            <div className="sample-hint">
              <strong>💡 Tip:</strong> Create a simple .txt file with lines like:<br />
              <code>Name: Priya Sharma | Age: 28 | Gender: Female | Income: 180000 | State: Maharashtra | Occupation: Farmer | Category: OBC</code>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════
            STEP 2 — Results
        ════════════════════════════════════════ */}
        {step === 2 && (
          <div className="results-layout">
            {/* Profile Card */}
            {profile && (
              <div className="card profile-card">
                <div className="card-header">
                  <span className="card-header-icon">👤</span>
                  <h2>Extracted Profile</h2>
                  <span className="nova-tag">via Nova Lite</span>
                </div>
                <div className="profile-grid">
                  {Object.entries(profile).map(([k, v]) => v != null && (
                    <div className="profile-field" key={k}>
                      <span className="field-label">{k.replace(/_/g, " ")}</span>
                      <span className="field-value">
                        {k === "income" ? `₹${Number(v).toLocaleString("en-IN")}` :
                         k === "disability" ? (v ? "Yes" : "No") : String(v)}
                      </span>
                    </div>
                  ))}
                </div>
                <button className="btn-ghost" onClick={() => { setStep(1); setFile(null); }}>← Upload Different Doc</button>
              </div>
            )}

            {/* Schemes */}
            <div className="schemes-panel">
              <div className="schemes-header">
                <h2>🏛️ Eligible Government Schemes</h2>
                <span className="count-badge">{schemes.length} Found</span>
              </div>
              {schemes.length === 0 ? (
                <div className="card empty-state">
                  <div style={{ fontSize: 48 }}>🔍</div>
                  <p>No schemes matched your profile. Try uploading a document with more details (income, occupation, category).</p>
                </div>
              ) : (
                <div className="schemes-grid">
                  {schemes.map((s, i) => (
                    <div className="scheme-card" key={i}>
                      <div className="scheme-top">
                        <span className="scheme-icon">{CATEGORY_ICON[s.category] || "📋"}</span>
                        <div className="scheme-meta">
                          <div className="scheme-category">{s.category}</div>
                          <span className="priority-badge" style={{ color: PRIORITY_COLOR[s.priority] }}>
                            ● {s.priority || "Medium"} Priority
                          </span>
                        </div>
                      </div>
                      <h3 className="scheme-name">{s.scheme_name}</h3>
                      <p className="scheme-reason">{s.reason}</p>
                      <div className="scheme-actions">
                        <button className="btn-primary small" onClick={() => handleApply(s)}>
                          ⚡ Auto Apply
                        </button>
                        <a className="btn-secondary small" href={s.apply_url} target="_blank" rel="noreferrer">
                          🔗 Portal
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════
            STEP 3 — Apply
        ════════════════════════════════════════ */}
        {step === 3 && selectedScheme && (
          <div className="results-layout">
            <div className="card apply-card">
              <button className="btn-ghost" onClick={() => setStep(2)}>← Back to Schemes</button>
              <h2 className="card-title" style={{ marginTop: 16 }}>
                ⚡ Auto-Apply: {selectedScheme.scheme_name}
              </h2>

              {!applyResult ? (
                <div className="loading-block">
                  <div className="pulse-circle" />
                  <p>Nova Act agent is preparing your application...</p>
                </div>
              ) : (
                <>
                  <div className={`status-banner ${applyResult.status === "error" ? "error" : "success"}`}>
                    {applyResult.status === "ready_to_apply" ? "✅ Application Ready!" : applyResult.status}
                  </div>

                  {applyResult.prefilled_fields && (
                    <div className="section">
                      <h3>📋 Pre-filled Fields</h3>
                      <div className="profile-grid">
                        {Object.entries(applyResult.prefilled_fields).map(([k, v]) => v != null && (
                          <div className="profile-field" key={k}>
                            <span className="field-label">{k.replace(/_/g, " ")}</span>
                            <span className="field-value">
                              {k === "annual_income" ? `₹${Number(v).toLocaleString("en-IN")}` :
                               k === "disability" ? (v ? "Yes" : "No") : String(v)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {applyResult.documents_needed && (
                    <div className="section">
                      <h3>📂 Documents Required</h3>
                      <ul className="doc-list">
                        {applyResult.documents_needed.map((d, i) => <li key={i}>📄 {d}</li>)}
                      </ul>
                    </div>
                  )}

                  {applyResult.next_steps && (
                    <div className="section">
                      <h3>🗺️ Next Steps</h3>
                      <ul className="steps-list">
                        {applyResult.next_steps.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}

                  {applyResult.apply_url && (
                    <a className="btn-primary" href={applyResult.apply_url} target="_blank" rel="noreferrer"
                       style={{ display: "inline-block", textDecoration: "none", textAlign: "center", marginTop: 16 }}>
                      🚀 Go to Application Portal →
                    </a>
                  )}

                  {applyResult.automation_status && (
                    <div className="automation-status">{applyResult.automation_status}</div>
                  )}
                </>
              )}
            </div>

            {/* Chat remains visible in step 3 */}
            <ChatPanel chatMessages={chatMessages} chatInput={chatInput}
              setChatInput={setChatInput} chatLoading={chatLoading}
              handleChat={handleChat} chatEndRef={chatEndRef} />
          </div>
        )}

        {/* Chat panel shown on step 2 alongside schemes */}
        {step === 2 && (
          <ChatPanel chatMessages={chatMessages} chatInput={chatInput}
            setChatInput={setChatInput} chatLoading={chatLoading}
            handleChat={handleChat} chatEndRef={chatEndRef} />
        )}
      </main>
    </div>
  );
}

// ── Chat Panel Component ──────────────────────
function ChatPanel({ chatMessages, chatInput, setChatInput, chatLoading, handleChat, chatEndRef }) {
  return (
    <div className="card chat-card">
      <div className="card-header">
        <span className="card-header-icon">💬</span>
        <h2>Ask Nova</h2>
        <span className="nova-tag">Nova Lite</span>
      </div>
      <div className="chat-messages">
        {chatMessages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <span className="bubble-label">{msg.role === "ai" ? "🤖 Nova" : "You"}</span>
            <div className="bubble-text">{msg.text}</div>
          </div>
        ))}
        {chatLoading && (
          <div className="chat-bubble ai">
            <span className="bubble-label">🤖 Nova</span>
            <div className="bubble-text typing"><span /><span /><span /></div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <div className="chat-input-row">
        <input className="chat-input" placeholder="Ask about any scheme..."
          value={chatInput} onChange={e => setChatInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleChat()} />
        <button className="btn-primary small" onClick={handleChat} disabled={chatLoading}>
          {chatLoading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}