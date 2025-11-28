import React, { useEffect, useState } from 'react';

function App() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetch('/api/alerts')
      .then(res => res.json())
      .then(setAlerts);
  }, []);

  return (
    <div style={{ padding: 32 }}>
      <h1>AI Intrusion & Anomaly Detector Dashboard</h1>
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Alert ID</th>
            <th>User</th>
            <th>Severity</th>
            <th>Score</th>
            <th>Reasons</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map(a => (
            <tr key={a.alert_id} style={{ background: a.severity === 'high' ? '#ffcccc' : a.severity === 'medium' ? '#fff0b3' : '#e6ffe6' }}>
              <td>{a.alert_id}</td>
              <td>{a.username}</td>
              <td>{a.severity}</td>
              <td>{a.score}</td>
              <td>{a.reasons.join(', ')}</td>
              <td>{a.status}</td>
              <td>{a.action || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
