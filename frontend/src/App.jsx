import React, { useEffect, useState } from 'react';
import './App.css';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [expandedAlert, setExpandedAlert] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showInvestigation, setShowInvestigation] = useState(false);
  const [stats, setStats] = useState({ critical: 0, high: 0, medium: 0, low: 0, info: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await fetch('/api/alerts');
      const data = await res.json();
      setAlerts(data);
      calculateStats(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    }
  };

  const calculateStats = (alertList) => {
    const counts = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    alertList.forEach(a => {
      if (counts.hasOwnProperty(a.severity)) {
        counts[a.severity]++;
      }
    });
    setStats(counts);
  };

  const filteredAlerts = alerts
    .filter(a => a.status !== 'resolved')
    .filter(a => filter === 'all' || a.severity === filter);

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#ff1744',
      high: '#ff6b6b',
      medium: '#ffa502',
      low: '#ffd93d',
      info: '#6bcf7f'
    };
    return colors[severity] || '#999';
  };

  const getSeverityBgColor = (severity) => {
    const colors = {
      critical: 'rgba(255, 23, 68, 0.1)',
      high: 'rgba(255, 107, 107, 0.1)',
      medium: 'rgba(255, 165, 2, 0.1)',
      low: 'rgba(255, 217, 61, 0.1)',
      info: 'rgba(107, 207, 127, 0.1)'
    };
    return colors[severity] || 'rgba(0, 0, 0, 0.05)';
  };

  const markResolved = (id) => {
    setAlerts(prev => prev.map(a => a.alert_id === id ? { ...a, status: 'resolved' } : a));
  };

  const getPieChartData = () => {
    return [
      { name: 'Critical', value: stats.critical, color: '#ff1744' },
      { name: 'High', value: stats.high, color: '#ff6b6b' },
      { name: 'Medium', value: stats.medium, color: '#ffa502' },
      { name: 'Low', value: stats.low, color: '#ffd93d' },
      { name: 'Info', value: stats.info, color: '#6bcf7f' }
    ].filter(d => d.value > 0);
  };

  const openInvestigation = (alert) => {
    setSelectedAlert(alert);
    setShowInvestigation(true);
  };

  const closeInvestigation = () => {
    setShowInvestigation(false);
    setSelectedAlert(null);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-content">
          <h1 className="header-title">
            <span className="icon">🛡️</span> AI Intrusion & Anomaly Detector
          </h1>
          <p className="header-subtitle">Real-time behavioral anomaly detection with advanced threat analysis</p>
        </div>
      </header>

      <main className="main-content">
        {/* Top Section: Stats + Pie Chart */}
        <section className="dashboard-top">
          {/* Left Side: Stats Cards */}
          <div className="stats-left">
            <h2 className="section-subtitle">Alert Summary</h2>
            <div className="stat-item critical-stat">
              <div className="stat-icon-lg">🔴</div>
              <div className="stat-info">
                <div className="stat-value-lg">{stats.critical}</div>
                <div className="stat-label-lg">Critical</div>
              </div>
            </div>
            <div className="stat-item high-stat">
              <div className="stat-icon-lg">⚠️</div>
              <div className="stat-info">
                <div className="stat-value-lg">{stats.high}</div>
                <div className="stat-label-lg">High</div>
              </div>
            </div>
            <div className="stat-item medium-stat">
              <div className="stat-icon-lg">⚡</div>
              <div className="stat-info">
                <div className="stat-value-lg">{stats.medium}</div>
                <div className="stat-label-lg">Medium</div>
              </div>
            </div>
            <div className="stat-item low-stat">
              <div className="stat-icon-lg">ℹ️</div>
              <div className="stat-info">
                <div className="stat-value-lg">{stats.low}</div>
                <div className="stat-label-lg">Low</div>
              </div>
            </div>
            <div className="stat-item info-stat">
              <div className="stat-icon-lg">ℹ️</div>
              <div className="stat-info">
                <div className="stat-value-lg">{stats.info}</div>
                <div className="stat-label-lg">Info</div>
              </div>
            </div>
          </div>

          {/* Right Side: Pie Chart */}
          <div className="pie-chart-container">
            <h2 className="section-subtitle">Risk Distribution</h2>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={getPieChartData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {getPieChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value} alerts`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="filter-section">
          <div className="filter-group">
            <label htmlFor="severity-filter">Filter by Severity:</label>
            <select
              id="severity-filter"
              value={filter}
              onChange={e => setFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Alerts</option>
              <option value="critical">🔴 Critical</option>
              <option value="high">🟠 High</option>
              <option value="medium">🟡 Medium</option>
              <option value="low">🟢 Low</option>
              <option value="info">🔵 Info</option>
            </select>
          </div>
          <div className="alert-count">Showing {filteredAlerts.length} alert(s)</div>
        </section>

        <section className="alerts-section">
          <h2 className="section-title">Active Alerts</h2>
          {filteredAlerts.length === 0 ? (
            <div className="no-alerts">
              <p>✓ No alerts to display</p>
            </div>
          ) : (
            <div className="alerts-container">
              {filteredAlerts.map((alert, idx) => (
                <div
                  key={alert.alert_id}
                  className="alert-card"
                  style={{
                    borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
                    background: getSeverityBgColor(alert.severity),
                    animation: `slideIn 0.5s ease-out ${idx * 0.05}s`
                  }}
                >
                  <div className="alert-header">
                    <div className="alert-title">
                      <span className="severity-badge" style={{ background: getSeverityColor(alert.severity) }}>
                        {alert.severity.toUpperCase()}
                      </span>
                      <span className="alert-id">{alert.alert_id}</span>
                      <span className="alert-status" style={{ color: getSeverityColor(alert.severity) }}>
                        {alert.status === 'resolved' ? '✓' : '●'}
                      </span>
                    </div>
                    <button
                      className="expand-btn"
                      onClick={() => setExpandedAlert(expandedAlert === alert.alert_id ? null : alert.alert_id)}
                    >
                      {expandedAlert === alert.alert_id ? '▼' : '▶'}
                    </button>
                  </div>

                  <div className="alert-summary">
                    <div className="summary-item">
                      <span className="label">User:</span>
                      <span className="value">{alert.username}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Score:</span>
                      <span className="value" style={{ color: getSeverityColor(alert.severity) }}>
                        {alert.score.toFixed(2)}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Action:</span>
                      <span className="value action-badge" style={{ background: getSeverityColor(alert.severity) + '30' }}>
                        {alert.action || 'monitor'}
                      </span>
                    </div>
                  </div>

                  {expandedAlert === alert.alert_id && (
                    <div className="alert-details">
                      <div className="details-section">
                        <h4>Risk Factors:</h4>
                        <ul>
                          {alert.reasons.map((reason, i) => (
                            <li key={i}>
                              <span className="factor-icon">🔹</span> {reason}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="details-section">
                        <h4>Detection Details:</h4>
                        <div className="details-grid">
                          <div>
                            <strong>Created:</strong> {new Date(alert.created_at).toLocaleString()}
                          </div>
                          <div>
                            <strong>Risk Factors:</strong> {alert.risk_factors.join(', ')}
                          </div>
                        </div>
                      </div>

                      <div className="action-buttons">
                        {alert.status !== 'resolved' && (
                          <button
                            className="btn btn-resolve"
                            onClick={() => markResolved(alert.alert_id)}
                          >
                            ✓ Mark as Resolved
                          </button>
                        )}
                        <button
                          className="btn btn-investigate"
                          onClick={() => openInvestigation(alert)}
                        >
                          🔍 Investigate
                        </button>
                        <button className="btn btn-isolate">🔒 Isolate Account</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Investigation Modal */}
      {showInvestigation && selectedAlert && (
        <div className="modal-overlay" onClick={closeInvestigation}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeInvestigation}>✕</button>
            
            <h2 className="modal-title">📋 Investigation Report</h2>
            
            <div className="investigation-grid">
              <div className="investigation-card alert-overview">
                <h3>Alert Overview</h3>
                <div className="investigation-item">
                  <span className="label">Alert ID:</span>
                  <span className="value">{selectedAlert.alert_id}</span>
                </div>
                <div className="investigation-item">
                  <span className="label">User:</span>
                  <span className="value">{selectedAlert.username}</span>
                </div>
                <div className="investigation-item">
                  <span className="label">Severity:</span>
                  <span className="value" style={{ color: getSeverityColor(selectedAlert.severity), fontWeight: 'bold' }}>
                    {selectedAlert.severity.toUpperCase()}
                  </span>
                </div>
                <div className="investigation-item">
                  <span className="label">Risk Score:</span>
                  <span className="value risk-score">{(selectedAlert.score * 100).toFixed(0)}%</span>
                </div>
                <div className="investigation-item">
                  <span className="label">Status:</span>
                  <span className="value" style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    background: '#f0f0f0',
                    color: '#333'
                  }}>
                    {selectedAlert.status}
                  </span>
                </div>
              </div>

              <div className="investigation-card threat-analysis">
                <h3>Threat Analysis</h3>
                <div className="threat-list">
                  {selectedAlert.reasons.map((reason, idx) => (
                    <div key={idx} className="threat-item">
                      <span className="threat-icon">🚨</span>
                      <div className="threat-content">
                        <p className="threat-reason">{reason}</p>
                        <p className="threat-risk-factor">Risk Factor: {selectedAlert.risk_factors[idx] || 'N/A'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="investigation-card timeline">
                <h3>Timeline</h3>
                <div className="timeline-item">
                  <span className="timeline-time">Alert Created</span>
                  <span className="timeline-date">{new Date(selectedAlert.created_at).toLocaleString()}</span>
                </div>
                <div className="timeline-item">
                  <span className="timeline-time">Current Status</span>
                  <span className="timeline-date">{selectedAlert.status}</span>
                </div>
              </div>

              <div className="investigation-card recommended-actions">
                <h3>Recommended Actions</h3>
                <div className="action-list">
                  <div className="action-item action-item-1">
                    <span className="action-number">1</span>
                    <span className="action-text">Review user access logs</span>
                  </div>
                  <div className="action-item action-item-2">
                    <span className="action-number">2</span>
                    <span className="action-text">Verify device fingerprint</span>
                  </div>
                  <div className="action-item action-item-3">
                    <span className="action-number">3</span>
                    <span className="action-text">Check location inconsistencies</span>
                  </div>
                  <div className="action-item action-item-4">
                    <span className="action-number">4</span>
                    <span className="action-text">
                      {selectedAlert.action === 'lock_account' ? 'Isolation required' : 'Re-authentication required'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="investigation-card confidence">
                <h3>Confidence Metrics</h3>
                <div className="confidence-bar">
                  <div className="confidence-label">Detection Confidence</div>
                  <div className="confidence-meter">
                    <div 
                      className="confidence-fill" 
                      style={{ 
                        width: `${selectedAlert.score * 100}%`,
                        background: getSeverityColor(selectedAlert.severity)
                      }}
                    ></div>
                  </div>
                  <div className="confidence-value">{(selectedAlert.score * 100).toFixed(0)}%</div>
                </div>
              </div>

              <div className="investigation-card resolution">
                <h3>Resolution</h3>
                <div className="resolution-buttons">
                  <button className="btn-resolution resolve-now">
                    ✓ Resolve Now
                  </button>
                  <button className="btn-resolution isolate-now">
                    🔒 Lock Account
                  </button>
                  <button className="btn-resolution lock-now">
                    🚫 Deny Access
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <footer className="footer">
        <p>AI Intrusion & Anomaly Detector v1.0 | Real-time Threat Detection System</p>
      </footer>
    </div>
  );
}

export default App;
