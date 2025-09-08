import React, { useState } from 'react';

function AdminPanel() {
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [showRemoveModal, setShowRemoveModal] = useState(null);
  const users = [
    { id: 1, name: 'Dr. Smith', role: 'Consultant', status: 'Active' },
    { id: 2, name: 'Patient A', role: 'Patient', status: 'Active' },
    { id: 3, name: 'Dr. Johnson', role: 'Consultant', status: 'Inactive' }
  ];

  const settings = [
    { name: 'Session Timeout', value: '30 minutes' },
    { name: 'Max Daily Sessions', value: '8 sessions' },
    { name: 'Escalation Threshold', value: 'High Risk' },
    { name: 'Data Retention', value: '90 days' }
  ];

  return (
    <div className="admin-panel-page">
      {/* Header */}
      <header className="dashboard-header">
        <div className="logo">
          <h2>🌲 TherapyBot</h2>
        </div>
        <div className="user-info">
          <span>Administrator Panel</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="admin-main">
        <div className="dashboard-panels">
          {/* User Management Panel */}
          <div className="dashboard-panel user-management-panel">
            <h3>User Management</h3>
            <div className="users-list">
              {users.map((user) => (
                <div key={user.id} className="user-item">
                  <div className="user-info">
                    <h4>{user.name}</h4>
                    <span className="user-role">{user.role}</span>
                    <span className={`user-status ${user.status.toLowerCase()}`}>
                      {user.status}
                    </span>
                  </div>
                  <div className="user-actions">
                    <button className="btn-primary">Edit</button>
                    <button className="btn-danger" onClick={() => setShowRemoveModal(user.id)}>Remove</button>
                  </div>
                </div>
              ))}
              <button className="btn-primary add-user-btn" onClick={() => setShowAddUserModal(true)}>Add New User</button>
            </div>
          </div>

          {/* Settings Panel */}
          <div className="dashboard-panel settings-panel">
            <h3>System Settings</h3>
            <div className="settings-list">
              {settings.map((setting, index) => (
                <div key={index} className="setting-item">
                  <div className="setting-info">
                    <h4>{setting.name}</h4>
                    <span className="setting-value">{setting.value}</span>
                  </div>
                  <button className="btn-primary">Configure</button>
                </div>
              ))}
              <div className="settings-actions">
                <button className="btn-success">Save Changes</button>
                <button className="btn-primary">Reset Defaults</button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="admin-footer">
        <div className="footer-info">
          <span>System Status: Online</span>
          <span>🔒 Admin Access Only</span>
        </div>
      </footer>
      
      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="modal-overlay" onClick={() => setShowAddUserModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add New User</h3>
            <div className="form-group">
              <input className="form-input" placeholder="Full Name" />
            </div>
            <div className="form-group">
              <select className="form-input">
                <option>Select Role</option>
                <option>Patient</option>
                <option>Consultant</option>
              </select>
            </div>
            <div className="modal-actions">
              <button className="btn-success" onClick={() => setShowAddUserModal(false)}>Add User</button>
              <button className="btn-primary" onClick={() => setShowAddUserModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      
      {/* Remove User Modal */}
      {showRemoveModal && (
        <div className="modal-overlay" onClick={() => setShowRemoveModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Remove User</h3>
            <p>Are you sure you want to remove this user? This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="btn-danger" onClick={() => setShowRemoveModal(null)}>Remove</button>
              <button className="btn-primary" onClick={() => setShowRemoveModal(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;