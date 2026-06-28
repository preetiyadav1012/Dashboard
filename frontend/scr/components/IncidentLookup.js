import React, { useState, useEffect, useMemo } from "react";
import "./IncidentLookup.css";
import Toast from "./Toast";
import { useToast } from "../hooks/useToast";
import { FiSearch, FiRefreshCw, FiDownload, FiAlertCircle, FiCheckCircle, FiClock, FiBarChart2, FiChevronLeft, FiChevronRight, FiCalendar } from "react-icons/fi";
import { api } from "../api";

const PAGE_SIZE = 8;

const displayVal = (field) => {
  if (!field) return "N/A";
  if (typeof field === "object" && field.display_value) return field.display_value;
  return String(field);
};

const priorityColor = (label = "") => {
  const l = label.toLowerCase();
  if (l.includes("critical")) return "critical";
  if (l.includes("high"))     return "high";
  if (l.includes("moderate")) return "moderate";
  if (l.includes("low"))      return "low";
  return "planning";
};

const stateColor = (label = "") => {
  const l = label.toLowerCase();
  if (l.includes("new"))      return "new";
  if (l.includes("progress")) return "in_progress";
  if (l.includes("hold"))     return "on_hold";
  if (l.includes("resolved")) return "resolved";
  if (l.includes("closed"))   return "closed";
  return "";
};

const BreakdownBar = ({ label, count, total, colorClass }) => (
  <div className="breakdown-row">
    <span className={`breakdown-label badge-${colorClass}`}>{label}</span>
    <div className="breakdown-bar-wrap">
      <div className={`breakdown-bar-fill bar-${colorClass}`}
        style={{ width: `${total ? (count / total) * 100 : 0}%` }} />
    </div>
    <span className="breakdown-count">{count}</span>
  </div>
);

const PRIORITY_ORDER = ["Critical", "High", "Moderate", "Low", "Planning"];

const IncidentLookup = () => {
  const [analysis, setAnalysis]               = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(true);
  const [analysisError, setAnalysisError]     = useState("");

  const [searchQuery, setSearchQuery]   = useState("");
  const [searchType, setSearchType]     = useState("incident_number");
  const [dateFrom, setDateFrom]         = useState("");
  const [dateTo, setDateTo]             = useState("");
  const [incidents, setIncidents]       = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError]   = useState("");
  const [currentPage, setCurrentPage]   = useState(1);

  const [selected, setSelected]         = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [tableSelected, setTableSelected] = useState(null);
  const [tableDetailLoading, setTableDetailLoading] = useState(false);

  const { toasts, addToast, removeToast } = useToast();

  useEffect(() => { loadAnalysis(); }, []);

  const loadAnalysis = async () => {
    setAnalysisLoading(true);
    setAnalysisError("");
    try {
      const res = await api.get(`/api/incidents/analysis`);
      setAnalysis(res.data);
    } catch (err) {
      setAnalysisError(err.response?.data?.error || "Failed to load incident analysis.");
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) { setSearchError("Enter a search query."); return; }
    setSearchLoading(true);
    setSearchError("");
    setIncidents([]);
    setSelected(null);
    setCurrentPage(1);
    try {
      const res = await api.post(`/api/incidents/search`, {
        query: searchQuery,
        search_type: searchType,
      });
      const list = res.data.incidents || [];
      setIncidents(list);
      if (!list.length) setSearchError("No incidents found for that query.");
      else addToast(`Found ${list.length} incident(s)`, "success");
    } catch (err) {
      setSearchError(err.response?.data?.error || "Search failed.");
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSelectIncident = async (number) => {
    if (selected?.number === number) { setSelected(null); return; }
    setDetailLoading(true);
    try {
      const res = await api.get(`/api/incidents/${number}`);
      setSelected(res.data.incident);
    } catch {
      setSelected(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleViewFromTable = async (number) => {
    if (tableSelected?.number === number) { setTableSelected(null); return; }
    setTableDetailLoading(true);
    try {
      const res = await api.get(`/api/incidents/${number}`);
      setTableSelected(res.data.incident);
    } catch {
      setTableSelected(null);
    } finally {
      setTableDetailLoading(false);
    }
  };

  /* Client-side date filter */
  const filteredIncidents = useMemo(() => {
    if (!dateFrom && !dateTo) return incidents;
    return incidents.filter((inc) => {
      const d = inc.sys_created_on ? inc.sys_created_on.slice(0, 10) : "";
      if (dateFrom && d < dateFrom) return false;
      if (dateTo   && d > dateTo)   return false;
      return true;
    });
  }, [incidents, dateFrom, dateTo]);

  const totalPages = Math.max(1, Math.ceil(filteredIncidents.length / PAGE_SIZE));
  const paginated  = filteredIncidents.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const handleExport = () => {
    const rows = [
      ["Number", "Title", "State", "Priority", "Category", "Assigned To", "Created"],
      ...filteredIncidents.map((i) => [
        i.number, i.short_description,
        displayVal(i.state), displayVal(i.priority),
        i.category || "", displayVal(i.assigned_to), i.sys_created_on,
      ]),
    ]
      .map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([rows], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url;
    a.download = `incidents_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    addToast("Incidents exported to CSV", "success");
  };

  const totalPri = analysis ? Object.values(analysis.priority_breakdown).reduce((a, b) => a + b, 0) : 0;
  const totalSt  = analysis ? Object.values(analysis.state_breakdown).reduce((a, b) => a + b, 0) : 0;

  return (
    <div className="incident-container">
      <Toast toasts={toasts} removeToast={removeToast} />

      {/* Analysis Report */}
      <div className="section-header">
        <FiBarChart2 size={22} />
        <h2>Incident Analysis Report</h2>
        <button className="icon-btn" onClick={loadAnalysis} title="Refresh">
          <FiRefreshCw className={analysisLoading ? "spinner" : ""} size={16} />
        </button>
      </div>

      {analysisError && <div className="error-banner">{analysisError}</div>}

      {analysisLoading ? (
        <div className="loading-row"><FiRefreshCw className="spinner" size={20} /><span>Loading analysis…</span></div>
      ) : analysis ? (
        <>
          <div className="analysis-summary-cards">
            <div className="summary-card blue">
              <FiBarChart2 size={28} />
              <div><p className="sc-label">Total Incidents</p><p className="sc-value">{analysis.total}</p></div>
            </div>
            <div className="summary-card red">
              <FiAlertCircle size={28} />
              <div><p className="sc-label">Critical</p><p className="sc-value">{analysis.priority_breakdown["Critical"] || 0}</p></div>
            </div>
            <div className="summary-card orange">
              <FiClock size={28} />
              <div><p className="sc-label">In Progress</p><p className="sc-value">{analysis.state_breakdown["In Progress"] || 0}</p></div>
            </div>
            <div className="summary-card green">
              <FiCheckCircle size={28} />
              <div>
                <p className="sc-label">Resolved / Closed</p>
                <p className="sc-value">{(analysis.state_breakdown["Resolved"] || 0) + (analysis.state_breakdown["Closed"] || 0)}</p>
              </div>
            </div>
          </div>

          <div className="analysis-breakdown-grid">
            <div className="breakdown-card">
              <h3>Priority Breakdown</h3>
              {PRIORITY_ORDER.filter((p) => analysis.priority_breakdown[p]).map((p) => (
                <BreakdownBar key={p} label={p} count={analysis.priority_breakdown[p]} total={totalPri} colorClass={priorityColor(p)} />
              ))}
            </div>
            <div className="breakdown-card">
              <h3>State Breakdown</h3>
              {Object.entries(analysis.state_breakdown).sort((a, b) => b[1] - a[1]).map(([s, c]) => (
                <BreakdownBar key={s} label={s} count={c} total={totalSt} colorClass={stateColor(s)} />
              ))}
            </div>
            <div className="breakdown-card">
              <h3>Category Breakdown</h3>
              {Object.entries(analysis.category_breakdown).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([cat, cnt]) => (
                <BreakdownBar key={cat} label={cat} count={cnt} total={analysis.total} colorClass="default" />
              ))}
            </div>
          </div>

          <div className="recent-incidents-section">
            <h3>Recent Incidents (Latest 10)</h3>
            <table className="incidents-table">
              <thead>
                <tr>
                  <th>Number</th><th>Description</th><th>Priority</th>
                  <th>State</th><th>Category</th><th>Assigned To</th>
                  <th>Created</th><th>Action</th>
                </tr>
              </thead>
              <tbody>
                {analysis.recent_incidents.map((inc) => (
                  <tr key={inc.sys_id}>
                    <td><span className="inc-number">{inc.number}</span></td>
                    <td className="inc-desc">{inc.short_description}</td>
                    <td><span className={`badge priority-${priorityColor(displayVal(inc.priority))}`}>{displayVal(inc.priority)}</span></td>
                    <td><span className={`badge state-${stateColor(displayVal(inc.state))}`}>{displayVal(inc.state)}</span></td>
                    <td>{inc.category || "—"}</td>
                    <td>{displayVal(inc.assigned_to)}</td>
                    <td className="inc-date">{inc.sys_created_on}</td>
                    <td><button className="view-btn" onClick={() => handleViewFromTable(inc.number)}>{tableSelected?.number === inc.number ? "Close" : "View"}</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {tableDetailLoading && (
            <div className="detail-loading"><FiRefreshCw className="spinner" /> Loading details…</div>
          )}
          {!tableDetailLoading && tableSelected && (
            <IncidentDetail incident={tableSelected} />
          )}
        </>
      ) : null}

      {/* Search Panel */}
      <div className="search-panel">
        <h3><FiSearch size={18} /> Search Incidents</h3>
        <div className="search-controls">
          <select value={searchType} onChange={(e) => setSearchType(e.target.value)} className="search-select">
            <option value="incident_number">Incident Number</option>
            <option value="short_description">Description</option>
            <option value="state">State</option>
            <option value="priority">Priority</option>
          </select>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder={`Search by ${searchType.replace("_", " ")}…`}
            className="search-input"
            disabled={searchLoading}
          />
          <button onClick={handleSearch} disabled={searchLoading} className="search-button">
            {searchLoading ? <FiRefreshCw className="spinner" /> : <FiSearch />}
            {searchLoading ? "Searching…" : "Search"}
          </button>
        </div>

        {/* Date filter */}
        {incidents.length > 0 && (
          <div className="date-filter">
            <FiCalendar size={14} />
            <span className="date-filter-label">Filter by date:</span>
            <input type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setCurrentPage(1); }}
              className="date-input" title="From date" />
            <span className="date-sep">→</span>
            <input type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setCurrentPage(1); }}
              className="date-input" title="To date" />
            {(dateFrom || dateTo) && (
              <button className="clear-date-btn" onClick={() => { setDateFrom(""); setDateTo(""); setCurrentPage(1); }}>
                Clear
              </button>
            )}
          </div>
        )}

        {searchError && <div className="error-banner" style={{ marginTop: "0.75rem" }}>{searchError}</div>}
      </div>

      {/* Search Results */}
      {filteredIncidents.length > 0 && (
        <div className="results-section">
          <div className="results-header">
            <h3>
              {filteredIncidents.length} incident(s)
              {(dateFrom || dateTo) && incidents.length !== filteredIncidents.length
                ? ` (filtered from ${incidents.length})` : ""}
            </h3>
            <button onClick={handleExport} className="export-button">
              <FiDownload /> Export CSV
            </button>
          </div>

          <div className="incidents-list">
            {paginated.map((inc) => (
              <div
                key={inc.sys_id}
                className={`incident-card ${selected?.number === inc.number ? "selected" : ""}`}
                onClick={() => handleSelectIncident(inc.number)}
              >
                <div className="incident-header-card">
                  <span className={`incident-number ${priorityColor(displayVal(inc.priority))}`}>{inc.number}</span>
                  <span className={`incident-status ${stateColor(displayVal(inc.state))}`}>{displayVal(inc.state)}</span>
                </div>
                <div className="incident-title">{inc.short_description}</div>
                <div className="incident-meta">
                  <span>Priority: <strong>{displayVal(inc.priority)}</strong></span>
                  <span>Category: <strong>{inc.category || "N/A"}</strong></span>
                  <span>Created: <strong>{inc.sys_created_on}</strong></span>
                </div>
                {selected?.number === inc.number && (
                  detailLoading
                    ? <div className="detail-loading"><FiRefreshCw className="spinner" /> Loading details…</div>
                    : selected && <IncidentDetail incident={selected} />
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button className="page-btn" onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1}>
                <FiChevronLeft /> Prev
              </button>
              <span className="page-info">Page {currentPage} of {totalPages}</span>
              <button className="page-btn" onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
                Next <FiChevronRight />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const IncidentDetail = ({ incident }) => {
  const fields = [
    { label: "Incident Number",   value: incident.number },
    { label: "Short Description", value: incident.short_description },
    { label: "Description",       value: incident.description },
    { label: "State",             value: displayVal(incident.state) },
    { label: "Priority",          value: displayVal(incident.priority) },
    { label: "Category",          value: incident.category },
    { label: "Subcategory",       value: incident.subcategory },
    { label: "Assigned To",       value: displayVal(incident.assigned_to) },
    { label: "Assignment Group",  value: displayVal(incident.assignment_group) },
    { label: "Caller",            value: displayVal(incident.caller_id) },
    { label: "Created",           value: incident.sys_created_on },
    { label: "Updated",           value: incident.sys_updated_on },
    { label: "Resolved At",       value: incident.resolved_at },
    { label: "Close Code",        value: incident.close_code },
    { label: "Close Notes",       value: incident.close_notes },
  ].filter((f) => f.value && f.value !== "N/A");

  return (
    <div className="incident-detail-panel">
      <h4>Full Incident Details</h4>
      <div className="detail-grid">
        {fields.map(({ label, value }) => (
          <div key={label} className="detail-row">
            <span className="detail-label">{label}</span>
            <span className="detail-value">{value}</span>
          </div>
        ))}
      </div>
      {incident.comments_and_work_notes && (
        <div className="work-notes-section">
          <h5>Comments &amp; Work Notes</h5>
          <pre className="work-notes">{incident.comments_and_work_notes}</pre>
        </div>
      )}
    </div>
  );
};

export default IncidentLookup;
