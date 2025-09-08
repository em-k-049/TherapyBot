import React from 'react';

function ConsultantDashboard() {
  const escalatedCases = [
    { id: 1, patient: 'Patient A', severity: 'High', time: '2 hours ago' },
    { id: 2, patient: 'Patient B', severity: 'Medium', time: '4 hours ago' },
    { id: 3, patient: 'Patient C', severity: 'High', time: '6 hours ago' }
  ];

  const analytics = {
    totalSessions: 156,
    activePatients: 23,
    avgResponseTime: '2.3 min',
    satisfactionRate: '94%'
  };

  return (
    <div className="consultant-dashboard-page">
      {/* Header */}
      <header className="dashboard-header">
        <div className="logo">
          <h2>🌲 TherapyBot</h2>
        </div>
        <div className="user-info">
          <span>Dr. Smith - Consultant</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="consultant-main">
        <div className="dashboard-panels">
          {/* Escalated Cases Panel */}
          <div className="dashboard-panel escalated-panel">
            <h3>Escalated Cases</h3>
            <div className="cases-list">
              {escalatedCases.map((case_) => (
                <div key={case_.id} className="case-item">
                  <div className="case-info">
                    <h4>{case_.patient}</h4>
                    <span className={`severity ${case_.severity.toLowerCase()}`}>
                      {case_.severity} Priority
                    </span>
                  </div>
                  <div className="case-time">{case_.time}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Analytics Panel */}
          <div className="dashboard-panel analytics-panel" onClick={() => setShowAnalyticsDetails(!showAnalyticsDetails)}>
            <h3>Analytics {showAnalyticsDetails ? '▼' : '▶'}</h3>
            <div className="analytics-grid">
              <div className="metric">
                <div className="metric-value">{analytics.totalSessions}</div>
                <div className="metric-label">Total Sessions</div>
              </div>
              <div className="metric">
                <div className="metric-value">{analytics.activePatients}</div>
                <div className="metric-label">Active Patients</div>
              </div>
              <div className="metric">
                <div className="metric-value">{analytics.avgResponseTime}</div>
                <div className="metric-label">Avg Response</div>
              </div>
              <div className="metric">
                <div className="metric-value">{analytics.satisfactionRate}</div>
                <div className="metric-label">Satisfaction</div>
              </div>
            </div>
            {showAnalyticsDetails && (
              <div className="analytics-details">
                <p>Detailed analytics: Response times improved by 15% this week. Patient satisfaction remains high across all consultants.</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="consultant-footer">
        <div className="footer-info">
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
          <span>🔒 Secure Dashboard</span>
        </div>
      </footer>
    </div>
  );
}

export default ConsultantDashboard;