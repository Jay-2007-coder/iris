import React, { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import './IrisAuth.css';

// In development: uses localhost. In production (Vercel): uses VITE_API_BASE env var.
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api';


// Tabs: 'login' | 'register' | 'manage'
const IrisAuth = ({ onAuthenticated }) => {
  const webcamRef = useRef(null);
  const [tab, setTab] = useState('login');
  const [username, setUsername] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const [statusType, setStatusType] = useState(''); // 'success' | 'error' | 'info'
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);

  // --- Helpers ---
  const setStatus = (msg, type = 'info') => { setStatusMsg(msg); setStatusType(type); };

  const capture = useCallback(() => {
    if (!webcamRef.current) return null;
    return webcamRef.current.getScreenshot();
  }, [webcamRef]);

  // Countdown then run an async action
  const withCountdown = (seconds, action) => {
    let remaining = seconds;
    setStatus(`Hold still... ${remaining}`, 'info');
    setCountdown(remaining);
    const timer = setInterval(() => {
      remaining--;
      if (remaining > 0) {
        setStatus(`Hold still... ${remaining}`, 'info');
        setCountdown(remaining);
      } else {
        clearInterval(timer);
        setCountdown(null);
        action();
      }
    }, 1000);
  };

  // --- Login ---
  const handleLogin = () => {
    withCountdown(3, async () => {
      const imageSrc = capture();
      if (!imageSrc) return;
      setLoading(true);
      setStatus('Authenticating your iris...', 'info');
      try {
        const res = await fetch(`${API_BASE}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageSrc })
        });
        const data = await res.json();
        if (data.success) {
          setStatus(`Identity confirmed! Welcome, ${data.username} (Score: ${data.score})`, 'success');
          setTimeout(() => onAuthenticated(data.username), 1500);
        } else {
          setStatus(data.message, 'error');
        }
      } catch {
        setStatus('Cannot reach Authentication Server. Is it running?', 'error');
      } finally {
        setLoading(false);
      }
    });
  };

  // --- Register ---
  const handleRegister = () => {
    if (!username.trim()) { setStatus('Please enter a username.', 'error'); return; }
    withCountdown(3, async () => {
      const imageSrc = capture();
      if (!imageSrc) return;
      setLoading(true);
      setStatus('Capturing iris pattern...', 'info');
      try {
        const res = await fetch(`${API_BASE}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, image: imageSrc })
        });
        const data = await res.json();
        if (data.success) {
          setStatus('Registered successfully! Switch to Login.', 'success');
          setUsername('');
        } else {
          setStatus(data.message, 'error');
        }
      } catch {
        setStatus('Cannot reach Authentication Server. Is it running?', 'error');
      } finally {
        setLoading(false);
      }
    });
  };

  // --- Management ---
  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_BASE}/users`);
      const data = await res.json();
      setUsers(data.users || []);
    } catch { setUsers([]); }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/logs`);
      const data = await res.json();
      setLogs(data.logs || []);
    } catch { setLogs([]); }
  };

  const handleDelete = async (uname) => {
    if (!window.confirm(`Delete user "${uname}"?`)) return;
    try {
      const res = await fetch(`${API_BASE}/delete`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: uname })
      });
      const data = await res.json();
      setStatus(data.message, data.success ? 'success' : 'error');
      fetchUsers();
    } catch {
      setStatus('Error deleting user.', 'error');
    }
  };

  useEffect(() => {
    if (tab === 'manage') {
      fetchUsers();
      fetchLogs();
    }
  }, [tab]);

  // --- Render ---
  const isBusy = loading || countdown !== null;

  return (
    <div className="auth-wrapper">
      <div className="auth-card glass-panel">

        {/* Header */}
        <div className="auth-header">
          <div className="iris-icon">👁️</div>
          <h1 className="auth-title">Iris Auth</h1>
          <p className="auth-subtitle">Biometric access control</p>
        </div>

        {/* Tabs */}
        <div className="auth-tabs">
          {['login', 'register', 'manage'].map(t => (
            <button
              key={t}
              className={`tab-btn ${tab === t ? 'active' : ''}`}
              onClick={() => { setTab(t); setStatusMsg(''); }}
            >
              {t === 'login' ? '🔑 Login' : t === 'register' ? '📋 Register' : '⚙️ Manage'}
            </button>
          ))}
        </div>

        {/* Camera (login + register tabs only) */}
        {tab !== 'manage' && (
          <div className="webcam-wrapper">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{ facingMode: 'user', width: 420, height: 280 }}
              className="webcam-feed"
            />
            {/* Corner brackets */}
            <div className="corner tl" /><div className="corner tr" />
            <div className="corner bl" /><div className="corner br" />
            {/* Scanning line */}
            <div className={`scan-line ${isBusy ? 'scanning' : ''}`} />
            {/* Countdown overlay */}
            {countdown !== null && (
              <div className="countdown-overlay">{countdown}</div>
            )}
          </div>
        )}

        {/* Status */}
        {statusMsg && (
          <p className={`auth-status ${statusType}`}>{statusMsg}</p>
        )}

        {/* --- Login Tab --- */}
        {tab === 'login' && (
          <div className="auth-form">
            <button onClick={handleLogin} disabled={isBusy} className="btn btn-primary">
              {isBusy ? 'Please wait...' : '🔓 Authenticate with Iris'}
            </button>
          </div>
        )}

        {/* --- Register Tab --- */}
        {tab === 'register' && (
          <div className="auth-form">
            <input
              type="text"
              placeholder="Choose a username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              className="auth-input"
              disabled={isBusy}
            />
            <button onClick={handleRegister} disabled={isBusy} className="btn btn-success">
              {isBusy ? 'Please wait...' : '📸 Capture & Register'}
            </button>
            <p className="auth-hint">Look straight at the camera. A 3-second countdown will begin.</p>
          </div>
        )}

        {/* --- Manage Tab --- */}
        {tab === 'manage' && (
          <div className="manage-panel">
            <h3 className="manage-heading">Registered Users</h3>
            {users.length === 0
              ? <p className="manage-empty">No users registered yet.</p>
              : <ul className="user-list">
                  {users.map(u => (
                    <li key={u} className="user-item">
                      <span>👤 {u}</span>
                      <button onClick={() => handleDelete(u)} className="btn btn-danger btn-sm">Delete</button>
                    </li>
                  ))}
                </ul>
            }

            <h3 className="manage-heading" style={{marginTop:'1.5rem'}}>Recent Logs</h3>
            {logs.length === 0
              ? <p className="manage-empty">No login attempts logged.</p>
              : <div className="log-table-wrapper">
                  <table className="log-table">
                    <thead><tr><th>User</th><th>Time</th><th>Status</th></tr></thead>
                    <tbody>
                      {logs.slice(0, 20).map((l, i) => (
                        <tr key={i}>
                          <td>{l.username}</td>
                          <td>{l.timestamp}</td>
                          <td className={l.status === 'Success' ? 'status-ok' : 'status-fail'}>{l.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default IrisAuth;
