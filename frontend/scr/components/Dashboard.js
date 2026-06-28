import React, { useState, useEffect } from "react";
import "./Dashboard.css";
import Toast from "./Toast";
import { useToast } from "../hooks/useToast";
import { FiRefreshCw, FiDownload } from "react-icons/fi";
import { api } from "../api";

const STATUS_COLORS = {
  "UI Draft":       "#a0aec0",
  "EDI Processing": "#4299e1",
  "EDI Complete":   "#48bb78",
  "EDI Accepted":   "#9f7aea",
};

/* ── SVG Donut Chart ── */
const DonutChart = ({ data }) => {
  const total = data.reduce((s, d) => s + d.count, 0);
  if (!total) return <p className="no-data">No claims data</p>;

  const R = 54;
  const C = 2 * Math.PI * R;
  let cumLen = 0;

  const slices = data.map((d) => {
    const len = (d.count / total) * C;
    const slice = {
      ...d,
      dashArray: `${len} ${C - len}`,
      dashOffset: -cumLen,
      color: STATUS_COLORS[d.status] || "#a0aec0",
    };
    cumLen += len;
    return slice;
  });

  return (
    <div className="donut-wrap">
      <svg viewBox="0 0 160 160" width="160" height="160">
        <circle
          cx="80"
          cy="80"
          r={R}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="22"
        />
        {slices.map((s, i) => (
          <circle
            key={i}
            cx="80"
            cy="80"
            r={R}
            fill="none"
            stroke={s.color}
            strokeWidth="22"
            strokeDasharray={s.dashArray}
            strokeDashoffset={s.dashOffset}
            transform="rotate(-90 80 80)"
          />
        ))}
        <text
          x="80"
          y="76"
          textAnchor="middle"
          fontSize="26"
          fontWeight="700"
          fill="#2d3748"
        >
          {total}
        </text>
        <text x="80" y="94" textAnchor="middle" fontSize="11" fill="#718096">
          claims
        </text>
      </svg>
      <div className="donut-legend">
        {slices.map((s, i) => (
          <div key={i} className="legend-item">
            <span className="legend-dot" style={{ background: s.color }} />
            <span className="legend-label">{s.status}</span>
            <span className="legend-val">
              {s.count} · {s.percentage}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ── Stat Card ── */
const StatCard = ({ label, value, icon, color }) => (
  <div className={`stat-card ${color}`}>
    <div className="stat-icon">{icon}</div>
    <div className="stat-content">
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
    </div>
  </div>
);

/* ── Dashboard ── */
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [chartData, setChart] = useState([]);
  const [claims, setClaims] = useState([]);
  const [auditLogs, setAudit] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reprocessingIds, setReprocessingIds] = useState(new Set());
  const { toasts, addToast, removeToast } = useToast();

  const fetchStats = async () => {
    try {
      const res = await api.get(`/api/dashboard/stats`);
      setStats(res.data.stats || {});
      setChart(res.data.chart_data || []);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to fetch stats");
    }
  };

  const fetchClaims = async () => {
    try {
      const res = await api.get(`/api/claims`);
      setClaims(res.data.claims || []);
    } catch {
      /* errors shown via stats fetch */
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await api.get(`/api/audit-logs`);
      setAudit(res.data.logs || []);
    } catch {
      /* non-critical */
    }
  };

  const loadAll = async () => {
    setLoading(true);
    setError("");
    await Promise.all([fetchStats(), fetchClaims(), fetchAuditLogs()]);
    setLoading(false);
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    loadAll();
  }, []);

  const handleReprocess = async (claimId) => {
    setReprocessingIds((prev) => new Set(prev).add(claimId));
    try {
      await api.post(`/api/claims/${claimId}/reprocess`);
      addToast(`Claim ${claimId} reprocessing — EDI Complete in 10 seconds`, "info", 11000);
      await Promise.all([fetchClaims(), fetchStats(), fetchAuditLogs()]);
      setTimeout(async () => {
        await Promise.all([fetchClaims(), fetchStats(), fetchAuditLogs()]);
        setReprocessingIds((prev) => { const s = new Set(prev); s.delete(claimId); return s; });
        addToast(`Claim ${claimId} is now EDI Complete`, "success");
      }, 11000);
    } catch (err) {
      setReprocessingIds((prev) => { const s = new Set(prev); s.delete(claimId); return s; });
      addToast(err.response?.data?.error || "Reprocess failed", "error");
    }
  };

  const handleExportCSV = () => {
    const rows = [
      [
        "ID",
        "Batch ID",
        "Claim #",
        "Member ID",
        "Status",
        "Amount",
        "Description",
        "Created",
        "Updated",
        "Notes",
      ],
      ...claims.map((c) => [
        c.id,
        c.batch_id,
        c.claim_number,
        c.member_id,
        c.status,
        c.amount,
        c.description,
        c.created_date,
        c.last_updated,
        c.notes,
      ]),
    ]
      .map((r) =>
        r.map((v) => `"${String(v ?? "").replace(/"/g, '""')}"`).join(","),
      )
      .join("\n");

    const blob = new Blob([rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `claims_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    addToast("Claims exported to CSV", "success");
  };

  return (
    <div className="dashboard-container">
      <Toast toasts={toasts} removeToast={removeToast} />

      {/* Header */}
      <div className="dashboard-header">
        <h2>Claims Dashboard</h2>
        <div className="header-actions">
          <button
            className="export-btn"
            onClick={handleExportCSV}
            disabled={!claims.length}
          >
            <FiDownload size={15} /> Export CSV
          </button>
          <button
            className="refresh-button"
            onClick={loadAll}
            disabled={loading}
          >
            <FiRefreshCw className={loading ? "spinner" : ""} size={15} />
            Refresh
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading-state">
          <div className="loader" />
          <p>Loading dashboard…</p>
        </div>
      ) : (
        <>
          {/* Stat Cards */}
          <div className="stats-grid">
            <StatCard
              label="Total Claims"
              value={stats.total_claims || 0}
              icon="📋"
              color="primary"
            />
            <StatCard
              label="EDI Complete"
              value={stats.edi_complete || 0}
              icon="✅"
              color="success"
            />
            <StatCard
              label="UI Draft"
              value={stats.ui_draft || 0}
              icon="📝"
              color="info"
            />
            <StatCard
              label="EDI Accepted"
              value={stats.edi_accepted || 0}
              icon="🔄"
              color="danger"
            />
            <StatCard
              label="Completion Rate"
              value={`${stats.success_rate || 0}%`}
              icon="📊"
              color="success"
            />
            <StatCard
              label="Avg Claim Value"
              value={claims.length
                ? `$${(claims.reduce((s, c) => s + Number(c.amount), 0) / claims.length).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                : "$0.00"}
              icon="💰"
              color="primary"
            />
            <StatCard
              label="Total Value"
              value={`$${claims.reduce((s, c) => s + Number(c.amount), 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              icon="📈"
              color="info"
            />
          </div>

          {/* Charts row */}
          <div className="charts-section">
            <div className="chart-card">
              <h3>Status Distribution</h3>
              {chartData.length ? (
                <DonutChart data={chartData} />
              ) : (
                <p className="no-data">No data</p>
              )}
            </div>

            <div className="chart-card">
              <h3>Quick Stats</h3>
              <div className="quick-stats">
                <div className="quick-stat-item">
                  <span className="qs-label">Avg Processing Time</span>
                  <span className="qs-value">
                    {stats.avg_processing_time || "N/A"}
                  </span>
                </div>
                <div className="quick-stat-item">
                  <span className="qs-label">Claims Last 24 h</span>
                  <span className="qs-value">{stats.claims_last_24h || 0}</span>
                </div>
                <div className="quick-stat-item">
                  <span className="qs-label">Active Incidents</span>
                  <span className="qs-value">
                    {stats.active_incidents || 0}
                  </span>
                </div>
                <div className="quick-stat-item">
                  <span className="qs-label">System Status</span>
                  <span className="qs-value status-badge approved">
                    Operational
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Claims Table */}
          <div className="claims-section">
            <div className="section-header-row">
              <h3>Claims Table</h3>
              <span className="claim-count">
                {claims.length} claim{claims.length !== 1 ? "s" : ""}
              </span>
            </div>
            {claims.length ? (
              <div className="table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Claim #</th>
                      <th>Member ID</th>
                      <th>Status</th>
                      <th>Amount</th>
                      <th>Description</th>
                      <th>Created</th>
                      <th>Notes</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {claims.map((c) => (
                      <tr key={c.id}>
                        <td className="mono">{c.id}</td>
                        <td className="mono">{c.claim_number}</td>
                        <td>{c.member_id}</td>
                        <td>
                          <span className={`status-badge status-${c.status.toLowerCase().replace(/\s+/g, "-")}`}>
                            {c.status}
                          </span>
                        </td>
                        <td className="amount">
                          $
                          {Number(c.amount).toLocaleString("en-US", {
                            minimumFractionDigits: 2,
                          })}
                        </td>
                        <td className="desc">{c.description}</td>
                        <td className="date">{c.created_date}</td>
                        <td className="notes">{c.notes}</td>
                        <td>
                          {c.status === "EDI Processing" && (
                            reprocessingIds.has(c.id) ? (
                              <span className="reprocessing-indicator">
                                <FiRefreshCw className="spinner" size={13} /> Processing…
                              </span>
                            ) : (
                              <button
                                className="reprocess-btn"
                                onClick={() => handleReprocess(c.id)}
                              >
                                🔄 Reprocess
                              </button>
                            )
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="no-data">No claims found.</p>
            )}
          </div>

          {/* Activity Timeline */}
          <div className="activity-section">
            <h3>Recent Activity</h3>
            {auditLogs.length ? (
              <div className="timeline">
                {auditLogs.slice(0, 5).map((log, i) => (
                  <div
                    key={i}
                    className={`timeline-item ${log.status === "success" ? "tl-success" : "tl-error"}`}
                  >
                    <div className="tl-dot" />
                    <div className="tl-body">
                      <span className="tl-action">{log.action}</span>
                      {log.details && (
                        <span className="tl-detail">{log.details}</span>
                      )}
                      <span className="tl-time">{log.created_at}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">
                No activity yet. Reprocess a claim to see logs here.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
