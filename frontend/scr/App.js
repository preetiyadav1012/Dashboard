import React, { useState } from "react";
import "./App.css";
import Chat from "./components/Chat";
import IncidentLookup from "./components/IncidentLookup";
import Dashboard from "./components/Dashboard";
import Assessment from "./components/Assessment";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [chatOpen, setChatOpen]   = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <span className="header-icon">📋</span>
        <div className="header-content">
          <h1>Claims Management Dashboard</h1>
          <p>Intelligent claim reprocessing powered by AI</p>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-button ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          📊 Dashboard
        </button>
        <button
          className={`nav-button ${activeTab === "incidents" ? "active" : ""}`}
          onClick={() => setActiveTab("incidents")}
        >
          🔍 Incident Lookup
        </button>
        <button
          className={`nav-button ${activeTab === "assessment" ? "active" : ""}`}
          onClick={() => setActiveTab("assessment")}
        >
          📝 Assessment
        </button>
      </nav>

      <main className="app-main">
        {activeTab === "dashboard"  && <Dashboard />}
        {activeTab === "incidents"  && <IncidentLookup />}
        {activeTab === "assessment" && <Assessment />}
      </main>

      <footer className="app-footer">
        <p>© 2026 Claims Management System | Powered by AI Agent</p>
      </footer>

      {/* ── Floating Chat Panel ── */}
      <div className={`floating-panel ${chatOpen ? "panel-open" : "panel-closed"}`}>
        <button className="floating-panel-header" onClick={() => setChatOpen(!chatOpen)}>
          <div className="panel-title">
            <span className="panel-status-dot" />
            <span>💬 Claims Agent</span>
          </div>
          <span className="panel-chevron">{chatOpen ? "▼" : "▲"}</span>
        </button>
        <div className="floating-panel-body">
          <Chat />
        </div>
      </div>
    </div>
  );
}

export default App;
