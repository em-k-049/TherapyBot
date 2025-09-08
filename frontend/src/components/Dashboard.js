import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Add CSS for pulse animation
const pulseKeyframes = `
@keyframes pulse {
  0% { box-shadow: 0 8px 32px rgba(47, 79, 47, 0.3); }
  50% { box-shadow: 0 8px 32px rgba(231, 76, 60, 0.6), 0 0 0 10px rgba(231, 76, 60, 0.1); }
  100% { box-shadow: 0 8px 32px rgba(47, 79, 47, 0.3); }
}
`;

// Inject CSS
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = pulseKeyframes;
  document.head.appendChild(style);
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Recharts color palette
const COLORS = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60', '#3498db', '#9b59b6'];

function Dashboard() {
  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [consultants, setConsultants] = useState([]);
  const [escalatedMessages, setEscalatedMessages] = useState([]);
  const [filteredMessages, setFilteredMessages] = useState([]);
  const [filters, setFilters] = useState({ dateFrom: '', dateTo: '', patient: '', riskLevel: '' });
  const [selectedCase, setSelectedCase] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsFilters, setAnalyticsFilters] = useState({ timeRange: 'week', ageGroup: '', gender: '' });
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [consentGiven, setConsentGiven] = useState(false);
  const [wellnessData, setWellnessData] = useState({ mood: 5, note: '' });
  const [wellnessLogs, setWellnessLogs] = useState([]);
  const [showWellnessForm, setShowWellnessForm] = useState(false);
  const [showPrivacySettings, setShowPrivacySettings] = useState(false);
  const [retentionStatus, setRetentionStatus] = useState(null);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [filteredAuditLogs, setFilteredAuditLogs] = useState([]);
  const [auditFilters, setAuditFilters] = useState({ user: '', action: '', dateFrom: '', dateTo: '' });
  const [showSettings, setShowSettings] = useState(false);
  const [retentionSettings, setRetentionSettings] = useState({ messages: 365, wellness: 730, audit: 1095, autoDelete: false });
  const mediaRecorderRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }
    
    // Check speech recognition support
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechSupported(!!window.SpeechRecognition);
    
    // Decode JWT to get user role (simplified)
    const payload = JSON.parse(atob(token.split('.')[1]));
    setUser({ role: payload.role, username: payload.sub });
    
    if (payload.role === 'admin') {
      fetchConsultants();
      fetchSystemMetrics();
      fetchAuditLogs();
    } else if (payload.role === 'consultant') {
      fetchEscalatedMessages();
      fetchAnalytics();
    } else if (payload.role === 'patient') {
      createSession();
      fetchWellnessLogs();
      fetchRetentionStatus();
    }
  }, [navigate]);

  const fetchConsultants = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/consultants`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setConsultants(data);
      }
    } catch (error) {
      console.error('Error fetching consultants:', error);
    }
  };

  const fetchEscalatedMessages = async () => {
    try {
      const response = await fetch(`${API_URL}/escalations/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        const sortedMessages = data.sort((a, b) => b.risk_score - a.risk_score);
        setEscalatedMessages(sortedMessages);
        setFilteredMessages(sortedMessages);
      } else {
        // Fallback to mock data
        const mockData = [
          { 
            id: 1, 
            content: 'I want to kill myself', 
            username: 'patient1', 
            created_at: '2024-01-15T10:30:00Z',
            risk_score: 0.95,
            session_id: 'session-1'
          },
          { 
            id: 2, 
            content: 'I feel like hurting myself', 
            username: 'patient2', 
            created_at: '2024-01-15T09:15:00Z',
            risk_score: 0.75,
            session_id: 'session-2'
          },
          { 
            id: 3, 
            content: 'I am very depressed', 
            username: 'patient3', 
            created_at: '2024-01-14T14:20:00Z',
            risk_score: 0.60,
            session_id: 'session-3'
          }
        ];
        setEscalatedMessages(mockData);
        setFilteredMessages(mockData);
      }
    } catch (error) {
      console.error('Error fetching escalations:', error);
    }
  };

  const createSession = async () => {
    // Create a new session for the patient
    setCurrentSession('temp-session-' + Date.now());
  };

  const fetchWellnessLogs = async () => {
    try {
      const response = await fetch(`${API_URL}/wellness/logs`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setWellnessLogs(data);
      }
    } catch (error) {
      console.error('Error fetching wellness logs:', error);
    }
  };

  const submitWellnessLog = async () => {
    try {
      const response = await fetch(`${API_URL}/wellness/log`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mood_score: wellnessData.mood,
          note: wellnessData.note || null
        })
      });
      
      if (response.ok) {
        setWellnessData({ mood: 5, note: '' });
        setShowWellnessForm(false);
        fetchWellnessLogs();
        alert('Wellness check-in saved!');
      }
    } catch (error) {
      console.error('Error submitting wellness log:', error);
    }
  };

  const getMoodTrendData = () => {
    return wellnessLogs.slice(-30).map(log => ({
      date: new Date(log.created_at).toLocaleDateString(),
      mood: log.mood_score
    }));
  };

  const deleteWellnessData = async () => {
    if (!window.confirm('Are you sure you want to delete all your wellness data? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/wellness/delete-all`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        setWellnessLogs([]);
        alert('All wellness data has been deleted.');
      } else {
        alert('Failed to delete wellness data.');
      }
    } catch (error) {
      console.error('Error deleting wellness data:', error);
      alert('Error deleting wellness data.');
    }
  };

  const recordAudio = async () => {
    if (isRecording || isListening) {
      stopRecording();
    } else {
      await startRecording();
    }
  };
  
  const processVoiceInput = async (transcribedText) => {
    try {
      const response = await fetch(`${API_URL}/messages/chat/voice`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: transcribedText })
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Check for error in response
        if (data.error) {
          alert(`AI Error: ${data.error}`);
          return;
        }
        
        // Add user message
        const userMessage = {
          content: transcribedText,
          timestamp: new Date().toLocaleTimeString(),
          isAI: false,
          isVoice: true
        };
        
        // Add AI response
        const aiMessage = {
          content: data.reply,
          timestamp: new Date().toLocaleTimeString(),
          isAI: true,
          isVoice: true
        };
        
        setMessages(prev => [...prev, userMessage, aiMessage]);
        
        // Speak AI response using Web Speech API
        speakText(data.reply);
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        alert(`Server Error: ${errorData.error || errorData.detail || 'Failed to get AI response'}`);
      }
    } catch (error) {
      console.error('Voice processing error:', error);
      alert('Voice processing failed: ' + error.message);
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 1;
      speechSynthesis.speak(utterance);
    }
  };

  const downloadChatHistory = () => {
    const chatData = {
      session_id: currentSession,
      user: user.username,
      timestamp: new Date().toISOString(),
      messages: messages.map(msg => ({
        content: msg.content,
        timestamp: msg.timestamp,
        sender: msg.isAI ? 'AI' : 'User',
        has_audio: !!msg.audioData
      }))
    };
    
    const dataStr = JSON.stringify(chatData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
  };

  const applyFilters = () => {
    let filtered = [...escalatedMessages];
    
    if (filters.dateFrom) {
      filtered = filtered.filter(msg => 
        new Date(msg.created_at) >= new Date(filters.dateFrom)
      );
    }
    
    if (filters.dateTo) {
      filtered = filtered.filter(msg => 
        new Date(msg.created_at) <= new Date(filters.dateTo + 'T23:59:59')
      );
    }
    
    if (filters.patient) {
      filtered = filtered.filter(msg => 
        msg.username.toLowerCase().includes(filters.patient.toLowerCase())
      );
    }
    
    if (filters.riskLevel) {
      const minScore = parseFloat(filters.riskLevel);
      filtered = filtered.filter(msg => (msg.risk_score || 0.5) >= minScore);
    }
    
    setFilteredMessages(filtered);
  };

  const clearFilters = () => {
    setFilters({ dateFrom: '', dateTo: '', patient: '', riskLevel: '' });
    setFilteredMessages(escalatedMessages);
  };

  const handleRowClick = (caseItem) => {
    setSelectedCase(caseItem);
  };

  const closeDetails = () => {
    setSelectedCase(null);
  };

  const fetchAnalytics = async () => {
    try {
      const [trendsRes, patternsRes, riskRes] = await Promise.all([
        fetch(`${API_URL}/analytics/trends?period=${analyticsFilters.timeRange}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${API_URL}/analytics/patterns`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${API_URL}/analytics/risk-distribution`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);
      
      const trends = trendsRes.ok ? await trendsRes.json() : null;
      const patterns = patternsRes.ok ? await patternsRes.json() : null;
      const riskDist = riskRes.ok ? await riskRes.json() : null;
      
      setAnalyticsData({
        trends: trends ? trends.labels.map((label, i) => ({
          name: label,
          escalations: trends.datasets[0].data[i]
        })) : [
          { name: 'Week 1', escalations: 12 },
          { name: 'Week 2', escalations: 19 },
          { name: 'Week 3', escalations: 15 },
          { name: 'Week 4', escalations: 22 }
        ],
        patterns: patterns ? patterns.labels.map((label, i) => ({
          name: label,
          value: patterns.datasets[0].data[i]
        })) : [
          { name: 'Self Harm', value: 35 },
          { name: 'Depression', value: 25 },
          { name: 'Anxiety', value: 20 },
          { name: 'Substance Abuse', value: 20 }
        ],
        riskDistribution: riskDist ? riskDist.labels.map((label, i) => ({
          name: label,
          count: riskDist.datasets[0].data[i]
        })) : [
          { name: 'Low', count: 10 },
          { name: 'Moderate', count: 15 },
          { name: 'High', count: 20 },
          { name: 'Critical', count: 8 }
        ]
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const applyAnalyticsFilters = () => {
    fetchAnalytics();
  };

  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/metrics`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data);
      } else {
        // Fallback mock data
        setSystemMetrics({
          total_users: 1247,
          active_sessions: 23,
          total_escalations: 89,
          critical_cases: 12,
          consultants_online: 5,
          avg_response_time: 8.5
        });
      }
    } catch (error) {
      console.error('Error fetching system metrics:', error);
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/audit-logs?limit=100`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAuditLogs(data);
        setFilteredAuditLogs(data);
      } else {
        // Fallback mock data
        const mockData = [
          { id: 1, user: 'consultant1', action: 'escalation_viewed', timestamp: '2024-01-15T10:30:00Z', metadata: { escalation_id: 'esc-123' } },
          { id: 2, user: 'admin', action: 'role_changed', timestamp: '2024-01-15T09:15:00Z', metadata: { target_user: 'user123', new_role: 'consultant' } },
          { id: 3, user: 'patient1', action: 'message_sent', timestamp: '2024-01-15T08:45:00Z', metadata: { escalated: true } },
          { id: 4, user: 'consultant2', action: 'wellness_log_created', timestamp: '2024-01-14T16:20:00Z', metadata: { mood_score: 7 } },
          { id: 5, user: 'admin', action: 'retention_settings_updated', timestamp: '2024-01-14T14:10:00Z', metadata: { messages_days: 365 } }
        ];
        setAuditLogs(mockData);
        setFilteredAuditLogs(mockData);
      }
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    }
  };

  const applyAuditFilters = () => {
    let filtered = [...auditLogs];
    
    if (auditFilters.user) {
      filtered = filtered.filter(log => 
        log.user && log.user.toLowerCase().includes(auditFilters.user.toLowerCase())
      );
    }
    
    if (auditFilters.action) {
      filtered = filtered.filter(log => 
        log.action.toLowerCase().includes(auditFilters.action.toLowerCase())
      );
    }
    
    if (auditFilters.dateFrom) {
      filtered = filtered.filter(log => 
        new Date(log.timestamp) >= new Date(auditFilters.dateFrom)
      );
    }
    
    if (auditFilters.dateTo) {
      filtered = filtered.filter(log => 
        new Date(log.timestamp) <= new Date(auditFilters.dateTo + 'T23:59:59')
      );
    }
    
    setFilteredAuditLogs(filtered);
  };

  const clearAuditFilters = () => {
    setAuditFilters({ user: '', action: '', dateFrom: '', dateTo: '' });
    setFilteredAuditLogs(auditLogs);
  };

  const updateRetentionSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/settings/retention`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(retentionSettings)
      });
      if (response.ok) {
        alert('Retention settings updated successfully');
        setShowSettings(false);
        if (retentionSettings.autoDelete) {
          alert('Auto-delete has been enabled. Old data will be automatically purged.');
        }
      }
    } catch (error) {
      console.error('Error updating retention settings:', error);
    }
  };

  const getActionBadgeColor = (action) => {
    const colors = {
      'login': '#3498db',
      'message_sent': '#27ae60',
      'escalation_viewed': '#f39c12',
      'role_changed': '#9b59b6',
      'wellness_log_created': '#17a2b8',
      'retention_settings_updated': '#e74c3c'
    };
    return colors[action] || '#95a5a6';
  };

  const fetchRetentionStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/privacy/retention-status`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRetentionStatus(data);
      }
    } catch (error) {
      console.error('Error fetching retention status:', error);
    }
  };

  const exportUserData = async () => {
    try {
      const response = await fetch(`${API_URL}/privacy/export`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `therapybot_data_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
        alert('Data export downloaded successfully!');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data.');
    }
  };

  const deleteUserData = async (type) => {
    const confirmMessage = type === 'account' 
      ? 'Are you sure you want to delete your entire account? This action cannot be undone.'
      : 'Are you sure you want to delete all your messages? This action cannot be undone.';
    
    if (!window.confirm(confirmMessage)) return;
    
    try {
      const endpoint = type === 'account' ? '/privacy/account' : '/privacy/messages';
      const method = 'DELETE';
      const body = undefined; // DELETE requests don't need body
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ Success: ${data.message}`);
        if (type === 'account') {
          localStorage.removeItem('token');
          navigate('/');
        } else {
          setMessages([]);
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Delete failed:', response.status, errorData);
        alert(`❌ Failed to delete data: ${errorData.detail || errorData.message || 'Server error'}`);
      }
    } catch (error) {
      console.error('Error deleting data:', error);
      alert(`❌ Failed to delete data: ${error.message}`);
    }
  };

  const getRiskLevel = (score) => {
    if (score >= 0.8) return { level: 'Critical', color: '#e74c3c' };
    if (score >= 0.6) return { level: 'High', color: '#f39c12' };
    return { level: 'Moderate', color: '#f1c40f' };
  };

  const startRecording = async () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge for voice features.');
      return;
    }
    
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
        setIsRecording(true);
        setTranscript('');
      };
      
      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscript(finalTranscript + interimTranscript);
        
        if (finalTranscript) {
          processVoiceInput(finalTranscript);
        }
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setIsRecording(false);
        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please allow microphone access and try again.');
        } else {
          alert('Speech recognition failed. Please try again.');
        }
      };
      
      recognition.onend = () => {
        setIsListening(false);
        setIsRecording(false);
      };
      
      recognitionRef.current = recognition;
      recognition.start();
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      alert('Failed to start voice recognition');
    }
  };
  
  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    setIsRecording(false);
  };
  
  const playAudio = (audioData) => {
    const audio = new Audio(`data:audio/mpeg;base64,${audioData}`);
    audio.play();
  };

  const sendMessage = async (messageText = null, isVoice = false) => {
    const message = messageText || newMessage.trim();
    if (!message) return;
    
    try {
      const endpoint = isVoice ? '/messages/voice-chat' : '/messages/chat';
      const payload = isVoice ? 
        { message, return_audio: true } : 
        { message };
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Add user message
        const userMessage = {
          content: data.user_message,
          timestamp: new Date().toLocaleTimeString(),
          isAI: false,
          isVoice
        };
        
        // Add AI response
        const aiMessage = {
          content: data.ai_response,
          timestamp: new Date().toLocaleTimeString(),
          isAI: true,
          audioData: data.ai_audio,
          isVoice
        };
        
        setMessages(prev => [...prev, userMessage, aiMessage]);
        
        // Auto-play AI audio for voice conversations
        if (data.ai_audio && isVoice) {
          setTimeout(() => playAudio(data.ai_audio), 500);
        }
      } else {
        alert('Failed to send message');
      }
    } catch (error) {
      console.error('Send message error:', error);
      alert('Error sending message');
    }
    
    if (!messageText) setNewMessage('');
  };

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  if (!user) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>TherapyBot - {user.role.charAt(0).toUpperCase() + user.role.slice(1)} Dashboard</h1>
        <button onClick={logout} className="btn-logout">Logout</button>
      </div>

      {user.role === 'patient' && (
        <div>
          {/* Patient Dashboard Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px', borderBottom: '2px solid #e1e8ed' }}>
            <h2>Patient Dashboard</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => setShowWellnessForm(true)} 
                style={{ padding: '8px 16px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                🌟 Wellness Check-in
              </button>
              <button 
                onClick={() => setShowHistory(!showHistory)} 
                style={{ padding: '8px 16px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                📋 {showHistory ? 'Hide' : 'Show'} History
              </button>
              <button 
                onClick={() => setShowPrivacySettings(true)} 
                style={{ padding: '8px 16px', backgroundColor: '#e74c3c', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                🔒 Privacy Settings
              </button>
            </div>
          </div>

          {/* Wellness Check-in Form */}
          {showWellnessForm && (
            <div style={{ 
              position: 'fixed', 
              top: 0, 
              left: 0, 
              right: 0, 
              bottom: 0, 
              backgroundColor: 'rgba(0,0,0,0.5)', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              zIndex: 1000
            }}>
              <div style={{ 
                backgroundColor: 'white', 
                padding: '30px', 
                borderRadius: '12px', 
                maxWidth: '500px', 
                width: '90%'
              }}>
                <h3>Daily Wellness Check-in</h3>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>How are you feeling today? (1-10)</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={wellnessData.mood}
                    onChange={(e) => setWellnessData({...wellnessData, mood: parseInt(e.target.value)})}
                    style={{ width: '100%', marginBottom: '10px' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#7f8c8d' }}>
                    <span>😢 Very Low</span>
                    <span style={{ fontWeight: 'bold', fontSize: '16px' }}>{wellnessData.mood}</span>
                    <span>😊 Excellent</span>
                  </div>
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Optional Note:</label>
                  <textarea
                    value={wellnessData.note}
                    onChange={(e) => setWellnessData({...wellnessData, note: e.target.value})}
                    placeholder="How are you feeling? Any thoughts to share?"
                    style={{ width: '100%', height: '80px', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
                  />
                </div>
                
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button 
                    onClick={() => setShowWellnessForm(false)}
                    style={{ padding: '10px 20px', backgroundColor: '#95a5a6', color: 'white', border: 'none', borderRadius: '4px' }}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={submitWellnessLog}
                    style={{ padding: '10px 20px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '4px' }}
                  >
                    Save Check-in
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Mood Progress Chart */}
          {wellnessLogs.length > 0 && (
            <div style={{ padding: '20px', backgroundColor: '#f8f9fa', margin: '20px', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>Your Mood Progress</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    onClick={deleteWellnessData}
                    style={{ 
                      padding: '6px 12px', 
                      backgroundColor: '#e74c3c', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}
                  >
                    🗑️ Delete Data
                  </button>
                </div>
              </div>
              
              <div style={{ height: '300px', marginBottom: '20px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={getMoodTrendData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 10]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="mood" stroke="#3498db" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', textAlign: 'center' }}>
                <div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3498db' }}>
                    {wellnessLogs.length}
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Total Entries</div>
                </div>
                <div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#27ae60' }}>
                    {(wellnessLogs.reduce((sum, log) => sum + log.mood_score, 0) / wellnessLogs.length).toFixed(1)}
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Average Mood</div>
                </div>
                <div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f39c12' }}>
                    {Math.max(...wellnessLogs.map(log => log.mood_score))}
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Best Day</div>
                </div>
                <div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#e74c3c' }}>
                    {wellnessLogs.filter(log => new Date(log.created_at) >= new Date(Date.now() - 7*24*60*60*1000)).length}
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f8c8d' }}>This Week</div>
                </div>
              </div>
            </div>
          )}

          {/* Privacy Settings Modal */}
          {showPrivacySettings && (
            <div style={{ 
              position: 'fixed', 
              top: 0, 
              left: 0, 
              right: 0, 
              bottom: 0, 
              backgroundColor: 'rgba(0,0,0,0.5)', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              zIndex: 1000
            }}>
              <div style={{ 
                backgroundColor: 'white', 
                padding: '30px', 
                borderRadius: '12px', 
                maxWidth: '600px', 
                width: '90%',
                maxHeight: '80vh',
                overflowY: 'auto'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3>Privacy & Data Settings</h3>
                  <button onClick={() => setShowPrivacySettings(false)} style={{ 
                    background: 'none', 
                    border: 'none', 
                    fontSize: '24px', 
                    cursor: 'pointer',
                    color: '#7f8c8d'
                  }}>
                    ×
                  </button>
                </div>
                
                {/* Data Export Section */}
                <div style={{ marginBottom: '25px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                  <h4 style={{ marginBottom: '10px' }}>Export Your Data</h4>
                  <p style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '15px' }}>
                    Download all your messages, wellness logs, and session data in JSON format.
                  </p>
                  <button 
                    onClick={exportUserData}
                    style={{ padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px' }}
                  >
                    📥 Export My Data
                  </button>
                </div>
                
                {/* Data Retention Status */}
                {retentionStatus && (
                  <div style={{ marginBottom: '25px', padding: '20px', backgroundColor: '#fff3cd', borderRadius: '8px', border: '1px solid #ffeaa7' }}>
                    <h4 style={{ marginBottom: '10px' }}>Data Retention Status</h4>
                    <div style={{ fontSize: '14px', marginBottom: '10px' }}>
                      <strong>Retention Policies:</strong>
                      <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                        <li>Messages: {retentionStatus.retention_policies.messages_days} days</li>
                        <li>Wellness Logs: {retentionStatus.retention_policies.wellness_days} days</li>
                      </ul>
                    </div>
                    {(retentionStatus.data_eligible_for_deletion.old_messages > 0 || retentionStatus.data_eligible_for_deletion.old_wellness_logs > 0) && (
                      <div style={{ fontSize: '14px', color: '#856404' }}>
                        <strong>Data eligible for auto-deletion:</strong>
                        <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                          {retentionStatus.data_eligible_for_deletion.old_messages > 0 && (
                            <li>{retentionStatus.data_eligible_for_deletion.old_messages} old messages</li>
                          )}
                          {retentionStatus.data_eligible_for_deletion.old_wellness_logs > 0 && (
                            <li>{retentionStatus.data_eligible_for_deletion.old_wellness_logs} old wellness logs</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Data Deletion Section */}
                <div style={{ marginBottom: '25px', padding: '20px', backgroundColor: '#f8d7da', borderRadius: '8px', border: '1px solid #f5c6cb' }}>
                  <h4 style={{ marginBottom: '10px', color: '#721c24' }}>Delete Your Data</h4>
                  <p style={{ fontSize: '14px', color: '#721c24', marginBottom: '15px' }}>
                    Permanently delete your data. This action cannot be undone.
                  </p>
                  <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    <button 
                      onClick={() => deleteUserData('messages')}
                      style={{ padding: '8px 16px', backgroundColor: '#f39c12', color: 'white', border: 'none', borderRadius: '4px', fontSize: '14px' }}
                    >
                      🗑️ Delete Messages Only
                    </button>
                    <button 
                      onClick={() => deleteUserData('account')}
                      style={{ padding: '8px 16px', backgroundColor: '#e74c3c', color: 'white', border: 'none', borderRadius: '4px', fontSize: '14px' }}
                    >
                      ⚠️ Delete Entire Account
                    </button>
                  </div>
                </div>
                
                <div style={{ textAlign: 'center', fontSize: '12px', color: '#7f8c8d' }}>
                  Your privacy is important to us. All data operations are logged for security purposes.
                </div>
              </div>
            </div>
          )}

          {/* Conversation History */}
          {showHistory && (
            <div style={{ padding: '20px', margin: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3>Conversation History</h3>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={consentGiven}
                    onChange={(e) => setConsentGiven(e.target.checked)}
                  />
                  I consent to viewing my conversation history
                </label>
              </div>
              
              {consentGiven ? (
                <div style={{ maxHeight: '300px', overflowY: 'auto', backgroundColor: 'white', padding: '15px', borderRadius: '8px' }}>
                  {messages.length === 0 ? (
                    <p style={{ textAlign: 'center', color: '#7f8c8d' }}>No conversation history yet</p>
                  ) : (
                    messages.map((msg, idx) => (
                      <div key={idx} style={{ marginBottom: '15px', padding: '10px', backgroundColor: msg.isAI ? '#e8f4fd' : '#f0f0f0', borderRadius: '8px' }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                          {msg.isAI ? '🤖 TherapyBot' : '👤 You'}
                        </div>
                        <div>{msg.content}</div>
                        <div style={{ fontSize: '12px', color: '#7f8c8d', marginTop: '5px' }}>
                          {msg.timestamp}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
                  Please provide consent to view your conversation history
                </div>
              )}
              
              <div style={{ marginTop: '15px', textAlign: 'right' }}>
                <button onClick={downloadChatHistory} style={{ padding: '6px 12px', backgroundColor: '#17a2b8', color: 'white', border: 'none', borderRadius: '4px' }}>
                  📥 Download History
                </button>
              </div>
            </div>
          )}

          {/* Voice-First Chat Interface */}
          <div className="chat-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px', borderBottom: '1px solid #e1e8ed', background: 'linear-gradient(135deg, #2F4F2F, #3C6B3C)' }}>
              <h3 style={{ color: 'white', margin: 0 }}>🎤 Voice Therapy Session</h3>
              <div style={{ color: 'white', fontSize: '14px' }}>
                {isRecording ? '🔴 Listening...' : isListening ? '🎙️ Processing...' : '🎙️ Ready to listen'}
              </div>
            </div>
            
            {/* Primary Voice Control */}
            <div style={{ 
              padding: '30px', 
              textAlign: 'center', 
              background: 'linear-gradient(135deg, #FAF0E6, #F5F5DC)',
              borderBottom: '2px solid #e1e8ed'
            }}>
              {!speechSupported ? (
                <div>
                  <div style={{ 
                    width: '120px',
                    height: '120px',
                    borderRadius: '50%',
                    border: '3px dashed #95a5a6',
                    color: '#95a5a6',
                    fontSize: '48px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto',
                    backgroundColor: '#f8f9fa'
                  }}>
                    🚫
                  </div>
                  <div style={{ marginTop: '15px', fontSize: '18px', color: '#e74c3c', fontWeight: '500' }}>
                    Voice Not Supported
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '14px', color: '#7f8c8d', maxWidth: '400px', margin: '8px auto' }}>
                    Your browser does not support speech recognition. Please use Chrome or Edge for voice features, or continue with text input below.
                  </div>
                </div>
              ) : (
                <div>
                  <button 
                    onClick={recordAudio}
                    style={{ 
                      width: '120px',
                      height: '120px',
                      borderRadius: '50%',
                      border: 'none',
                      background: isRecording ? 
                        'linear-gradient(135deg, #e74c3c, #c0392b)' : 
                        'linear-gradient(135deg, #2F4F2F, #1F3F1F)',
                      color: 'white',
                      fontSize: '48px',
                      cursor: 'pointer',
                      boxShadow: '0 8px 32px rgba(47, 79, 47, 0.3)',
                      transition: 'all 0.3s ease',
                      transform: isRecording ? 'scale(1.1)' : 'scale(1)',
                      animation: isRecording ? 'pulse 1.5s infinite' : 'none'
                    }}
                    title={isRecording ? 'Stop Recording' : 'Start Voice Conversation'}
                  >
                    {isRecording ? '⏹️' : '🎤'}
                  </button>
                  <div style={{ marginTop: '15px', fontSize: '18px', color: '#2F4F2F', fontWeight: '500' }}>
                    {isRecording ? 'Listening... Speak now' : 'Tap to start voice conversation'}
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '14px', color: '#8B5E3C' }}>
                    {isRecording ? 'Speech recognition active' : 'Your voice will be converted to text and sent to our AI therapist'}
                  </div>
                </div>
              )}
              
              {/* Live Transcription Display */}
              {speechSupported && (isRecording || transcript) && (
                <div style={{ 
                  marginTop: '20px', 
                  padding: '15px', 
                  backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                  borderRadius: '8px',
                  border: '2px solid #2F4F2F',
                  minHeight: '50px'
                }}>
                  <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>
                    {isRecording ? '🎙️ Live Transcription:' : '📝 Last Transcription:'}
                  </div>
                  <div style={{ fontSize: '16px', color: '#2F4F2F', fontStyle: transcript ? 'normal' : 'italic' }}>
                    {transcript || (isRecording ? 'Listening...' : 'No speech detected')}
                  </div>
                </div>
              )}
            </div>
            
            <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.isAI ? 'ai' : 'user'}`}>
                <div>
                  <div className={`message-bubble ${msg.isAI ? 'ai' : 'user'}`}>
                    {msg.content}
                    {msg.audioData && (
                      <button 
                        onClick={() => playAudio(msg.audioData)}
                        style={{ marginLeft: '10px', padding: '4px 8px', fontSize: '12px' }}
                      >
                        🔊 Play
                      </button>
                    )}
                  </div>
                  <div className="message-time">
                    {msg.timestamp}
                  </div>
                </div>
              </div>
            ))}
          </div>
          {/* Secondary Text Input */}
          <div style={{ 
            padding: '15px 20px', 
            background: 'rgba(139, 94, 60, 0.05)',
            borderTop: '1px solid #e1e8ed'
          }}>
            <div style={{ 
              fontSize: '14px', 
              color: '#8B5E3C', 
              marginBottom: '10px',
              textAlign: 'center'
            }}>
              ⌨️ Or type your message (text mode)
            </div>
            <div className="chat-input" style={{ background: 'transparent', padding: 0 }}>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message here..."
                style={{ 
                  background: 'rgba(255, 255, 255, 0.8)',
                  border: '2px solid #e1e8ed',
                  borderRadius: '25px'
                }}
              />
              <button 
                onClick={() => sendMessage()}
                className="btn-send"
                style={{
                  background: '#2F4F2F',
                  borderRadius: '25px'
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
      )}

      {user.role === 'admin' && (
        <div>
          {/* Admin Dashboard Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Admin Dashboard</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => setShowSettings(true)}
                style={{ padding: '8px 16px', backgroundColor: '#9b59b6', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                ⚙️ Settings
              </button>
              <button 
                onClick={() => { fetchSystemMetrics(); fetchAuditLogs(); }}
                style={{ padding: '8px 16px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                🔄 Refresh
              </button>
            </div>
          </div>

          {/* System Metrics */}
          {systemMetrics && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
              <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db' }}>{systemMetrics.total_users}</div>
                <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Total Users</div>
              </div>
              <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#27ae60' }}>{systemMetrics.active_sessions}</div>
                <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Active Sessions</div>
              </div>
              <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f39c12' }}>{systemMetrics.total_escalations}</div>
                <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Total Escalations</div>
              </div>
              <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e74c3c' }}>{systemMetrics.critical_cases}</div>
                <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Critical Cases</div>
              </div>
              <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#9b59b6' }}>{systemMetrics.consultants_online}</div>
                <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Consultants Online</div>
              </div>
              <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#17a2b8' }}>{systemMetrics.avg_response_time}m</div>
                <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Avg Response Time</div>
              </div>
            </div>
          )}

          {/* Audit Log */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #e9ecef' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>Audit Log ({filteredAuditLogs.length})</h3>
                <button onClick={fetchAuditLogs} style={{ padding: '6px 12px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px', fontSize: '12px' }}>
                  🔄 Refresh
                </button>
              </div>
            </div>
            
            {/* Audit Filters */}
            <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderBottom: '1px solid #e9ecef' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', alignItems: 'end' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '12px' }}>User:</label>
                  <input
                    type="text"
                    placeholder="Filter by user..."
                    value={auditFilters.user}
                    onChange={(e) => setAuditFilters({...auditFilters, user: e.target.value})}
                    style={{ width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '12px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '12px' }}>Action:</label>
                  <select
                    value={auditFilters.action}
                    onChange={(e) => setAuditFilters({...auditFilters, action: e.target.value})}
                    style={{ width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '12px' }}
                  >
                    <option value="">All Actions</option>
                    <option value="login">Login</option>
                    <option value="message_sent">Message Sent</option>
                    <option value="escalation_viewed">Escalation Viewed</option>
                    <option value="role_changed">Role Changed</option>
                    <option value="wellness_log_created">Wellness Log</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '12px' }}>From Date:</label>
                  <input
                    type="date"
                    value={auditFilters.dateFrom}
                    onChange={(e) => setAuditFilters({...auditFilters, dateFrom: e.target.value})}
                    style={{ width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '12px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '12px' }}>To Date:</label>
                  <input
                    type="date"
                    value={auditFilters.dateTo}
                    onChange={(e) => setAuditFilters({...auditFilters, dateTo: e.target.value})}
                    style={{ width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '12px' }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button onClick={applyAuditFilters} style={{ padding: '6px 12px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '4px', fontSize: '12px' }}>
                    Apply
                  </button>
                  <button onClick={clearAuditFilters} style={{ padding: '6px 12px', backgroundColor: '#95a5a6', color: 'white', border: 'none', borderRadius: '4px', fontSize: '12px' }}>
                    Clear
                  </button>
                </div>
              </div>
            </div>
            
            {/* Audit Table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold', fontSize: '12px', borderBottom: '2px solid #e9ecef' }}>User</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold', fontSize: '12px', borderBottom: '2px solid #e9ecef' }}>Action</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold', fontSize: '12px', borderBottom: '2px solid #e9ecef' }}>Details</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold', fontSize: '12px', borderBottom: '2px solid #e9ecef' }}>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAuditLogs.length === 0 ? (
                    <tr>
                      <td colSpan="4" style={{ padding: '40px', textAlign: 'center', color: '#7f8c8d' }}>No audit logs found</td>
                    </tr>
                  ) : (
                    filteredAuditLogs.map(log => (
                      <tr key={log.id} style={{ borderBottom: '1px solid #f8f9fa' }}>
                        <td style={{ padding: '12px', fontSize: '13px' }}>
                          <div style={{ fontWeight: '500' }}>{log.user || 'System'}</div>
                        </td>
                        <td style={{ padding: '12px', fontSize: '13px' }}>
                          <span style={{ 
                            backgroundColor: getActionBadgeColor(log.action), 
                            color: 'white', 
                            padding: '3px 8px', 
                            borderRadius: '12px', 
                            fontSize: '11px', 
                            fontWeight: 'bold' 
                          }}>
                            {log.action.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td style={{ padding: '12px', fontSize: '12px', color: '#7f8c8d', maxWidth: '300px' }}>
                          {log.metadata && Object.entries(log.metadata).map(([key, value]) => (
                            <div key={key}>
                              <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
                            </div>
                          ))}
                        </td>
                        <td style={{ padding: '12px', fontSize: '12px', color: '#7f8c8d' }}>
                          {new Date(log.timestamp).toLocaleDateString()}
                          <br />
                          <span style={{ fontSize: '11px' }}>
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Consultant Management */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #e9ecef' }}>
              <h3>Consultant Management</h3>
            </div>
            <div style={{ padding: '20px' }}>
              {consultants.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#7f8c8d', padding: '20px' }}>No consultants found</div>
              ) : (
                <div style={{ display: 'grid', gap: '15px' }}>
                  {consultants.map(consultant => (
                    <div key={consultant.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{consultant.username}</div>
                        <div style={{ fontSize: '14px', color: '#7f8c8d' }}>{consultant.email}</div>
                      </div>
                      <button style={{ padding: '6px 12px', backgroundColor: '#e74c3c', color: 'white', border: 'none', borderRadius: '4px' }}>
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Settings Modal */}
          {showSettings && (
            <div style={{ 
              position: 'fixed', 
              top: 0, 
              left: 0, 
              right: 0, 
              bottom: 0, 
              backgroundColor: 'rgba(0,0,0,0.5)', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              zIndex: 1000
            }}>
              <div style={{ 
                backgroundColor: 'white', 
                padding: '30px', 
                borderRadius: '12px', 
                maxWidth: '500px', 
                width: '90%'
              }}>
                <h3>Data Retention Settings</h3>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Message Retention (days):</label>
                  <input
                    type="number"
                    value={retentionSettings.messages}
                    onChange={(e) => setRetentionSettings({...retentionSettings, messages: parseInt(e.target.value)})}
                    style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  />
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Wellness Data Retention (days):</label>
                  <input
                    type="number"
                    value={retentionSettings.wellness}
                    onChange={(e) => setRetentionSettings({...retentionSettings, wellness: parseInt(e.target.value)})}
                    style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  />
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Audit Log Retention (days):</label>
                  <input
                    type="number"
                    value={retentionSettings.audit}
                    onChange={(e) => setRetentionSettings({...retentionSettings, audit: parseInt(e.target.value)})}
                    style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  />
                </div>
                
                <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 'bold' }}>
                    <input
                      type="checkbox"
                      checked={retentionSettings.autoDelete}
                      onChange={(e) => setRetentionSettings({...retentionSettings, autoDelete: e.target.checked})}
                    />
                    Enable Auto-Delete
                  </label>
                  <div style={{ fontSize: '12px', color: '#7f8c8d', marginTop: '5px' }}>
                    Automatically delete old data based on retention policies above
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button 
                    onClick={() => setShowSettings(false)}
                    style={{ padding: '10px 20px', backgroundColor: '#95a5a6', color: 'white', border: 'none', borderRadius: '4px' }}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={updateRetentionSettings}
                    style={{ padding: '10px 20px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '4px' }}
                  >
                    Save Settings
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {user.role === 'consultant' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Consultant Dashboard</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => setShowAnalytics(!showAnalytics)} 
                style={{ padding: '8px 16px', backgroundColor: '#9b59b6', color: 'white', border: 'none', borderRadius: '4px' }}
              >
                📊 {showAnalytics ? 'Hide' : 'Show'} Analytics
              </button>
              <button onClick={fetchEscalatedMessages} style={{ padding: '8px 16px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px' }}>
                🔄 Refresh
              </button>
            </div>
          </div>

          {/* Analytics Section */}
          {showAnalytics && analyticsData && (
            <div style={{ marginBottom: '30px' }}>
              <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                <h3 style={{ marginBottom: '15px' }}>Analytics Filters</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', alignItems: 'end' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Time Range:</label>
                    <select
                      value={analyticsFilters.timeRange}
                      onChange={(e) => setAnalyticsFilters({...analyticsFilters, timeRange: e.target.value})}
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    >
                      <option value="week">Last 4 Weeks</option>
                      <option value="month">Last 12 Months</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Age Group:</label>
                    <select
                      value={analyticsFilters.ageGroup}
                      onChange={(e) => setAnalyticsFilters({...analyticsFilters, ageGroup: e.target.value})}
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    >
                      <option value="">All Ages</option>
                      <option value="18-25">18-25</option>
                      <option value="26-35">26-35</option>
                      <option value="36-50">36-50</option>
                      <option value="50+">50+</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Gender:</label>
                    <select
                      value={analyticsFilters.gender}
                      onChange={(e) => setAnalyticsFilters({...analyticsFilters, gender: e.target.value})}
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    >
                      <option value="">All Genders</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <button 
                      onClick={applyAnalyticsFilters}
                      style={{ padding: '8px 16px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      Apply Filters
                    </button>
                  </div>
                </div>
              </div>

              {/* Analytics Charts */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '20px' }}>
                {/* Case Trends Chart */}
                <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                  <h4 style={{ marginBottom: '15px' }}>Case Trends</h4>
                  <div style={{ height: '250px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData.trends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="escalations" fill="#e74c3c" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Escalation Patterns Chart */}
                <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                  <h4 style={{ marginBottom: '15px' }}>Crisis Triggers</h4>
                  <div style={{ height: '250px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analyticsData.patterns}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {analyticsData.patterns.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Risk Distribution Chart */}
                <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                  <h4 style={{ marginBottom: '15px' }}>Risk Distribution</h4>
                  <div style={{ height: '250px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData.riskDistribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count">
                          {analyticsData.riskDistribution.map((entry, index) => {
                            const colors = { 'Low': '#27ae60', 'Moderate': '#f1c40f', 'High': '#f39c12', 'Critical': '#e74c3c' };
                            return <Cell key={`cell-${index}`} fill={colors[entry.name] || '#3498db'} />;
                          })}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Summary Statistics */}
                <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                  <h4 style={{ marginBottom: '15px' }}>Summary Statistics</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e74c3c' }}>
                        {filteredMessages.length}
                      </div>
                      <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Total Cases</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f39c12' }}>
                        {filteredMessages.filter(msg => (msg.risk_score || 0) >= 0.8).length}
                      </div>
                      <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Critical Cases</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db' }}>
                        {filteredMessages.length > 0 ? (filteredMessages.reduce((sum, msg) => sum + (msg.risk_score || 0.5), 0) / filteredMessages.length).toFixed(2) : '0.00'}
                      </div>
                      <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Avg Risk Score</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#27ae60' }}>
                        {new Date().toLocaleDateString()}
                      </div>
                      <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Last Updated</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <h3 style={{ marginBottom: '15px' }}>Escalated Cases ({filteredMessages.length})</h3>
          
          {/* Filters */}
          <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '15px' }}>Filters</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', alignItems: 'end' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>From Date:</label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>To Date:</label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Patient Name:</label>
                <input
                  type="text"
                  placeholder="Search patient..."
                  value={filters.patient}
                  onChange={(e) => setFilters({...filters, patient: e.target.value})}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Risk Level:</label>
                <select
                  value={filters.riskLevel}
                  onChange={(e) => setFilters({...filters, riskLevel: e.target.value})}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                >
                  <option value="">All Levels</option>
                  <option value="0.8">Critical (0.8+)</option>
                  <option value="0.6">High (0.6+)</option>
                  <option value="0.4">Moderate (0.4+)</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={applyFilters} style={{ padding: '8px 16px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  Apply
                </button>
                <button onClick={clearFilters} style={{ padding: '8px 16px', backgroundColor: '#95a5a6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  Clear
                </button>
              </div>
            </div>
          </div>
          
          {/* Escalated Cases Table */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            {filteredMessages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
                No escalated cases found
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #e9ecef' }}>
                      <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold' }}>Patient</th>
                      <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold' }}>Risk Level</th>
                      <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold' }}>Score</th>
                      <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold' }}>Date</th>
                      <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold' }}>Message Preview</th>
                      <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredMessages.map(msg => {
                      const risk = getRiskLevel(msg.risk_score || 0.5);
                      return (
                        <tr 
                          key={msg.id} 
                          onClick={() => handleRowClick(msg)}
                          style={{ 
                            borderBottom: '1px solid #e9ecef',
                            cursor: 'pointer',
                            backgroundColor: msg.risk_score >= 0.8 ? '#fdf2f2' : 'white'
                          }}
                          onMouseEnter={(e) => e.target.parentElement.style.backgroundColor = '#f8f9fa'}
                          onMouseLeave={(e) => e.target.parentElement.style.backgroundColor = msg.risk_score >= 0.8 ? '#fdf2f2' : 'white'}
                        >
                          <td style={{ padding: '15px', fontWeight: '500' }}>{msg.username}</td>
                          <td style={{ padding: '15px' }}>
                            <span style={{ 
                              backgroundColor: risk.color, 
                              color: 'white', 
                              padding: '4px 8px', 
                              borderRadius: '12px', 
                              fontSize: '12px', 
                              fontWeight: 'bold' 
                            }}>
                              {risk.level}
                            </span>
                          </td>
                          <td style={{ padding: '15px', fontWeight: 'bold', color: risk.color }}>
                            {(msg.risk_score || 0.5).toFixed(2)}
                          </td>
                          <td style={{ padding: '15px', color: '#7f8c8d', fontSize: '14px' }}>
                            {new Date(msg.created_at).toLocaleDateString()}
                            <br />
                            <span style={{ fontSize: '12px' }}>
                              {new Date(msg.created_at).toLocaleTimeString()}
                            </span>
                          </td>
                          <td style={{ padding: '15px', maxWidth: '300px' }}>
                            <div style={{ 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis', 
                              whiteSpace: 'nowrap',
                              fontSize: '14px'
                            }}>
                              {msg.content}
                            </div>
                          </td>
                          <td style={{ padding: '15px' }}>
                            {msg.risk_score >= 0.8 && (
                              <span style={{ 
                                backgroundColor: '#e74c3c', 
                                color: 'white', 
                                padding: '4px 8px', 
                                borderRadius: '12px', 
                                fontSize: '12px', 
                                fontWeight: 'bold',
                                animation: 'pulse 2s infinite'
                              }}>
                                URGENT
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
          
          {/* Case Details Modal */}
          {selectedCase && (
            <div style={{ 
              position: 'fixed', 
              top: 0, 
              left: 0, 
              right: 0, 
              bottom: 0, 
              backgroundColor: 'rgba(0,0,0,0.5)', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              zIndex: 1000
            }}>
              <div style={{ 
                backgroundColor: 'white', 
                padding: '30px', 
                borderRadius: '12px', 
                maxWidth: '600px', 
                width: '90%',
                maxHeight: '80vh',
                overflowY: 'auto'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h2>Case Details</h2>
                  <button onClick={closeDetails} style={{ 
                    background: 'none', 
                    border: 'none', 
                    fontSize: '24px', 
                    cursor: 'pointer',
                    color: '#7f8c8d'
                  }}>
                    ×
                  </button>
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <h3>Patient: {selectedCase.username}</h3>
                  <p><strong>Risk Score:</strong> {(selectedCase.risk_score || 0.5).toFixed(2)}</p>
                  <p><strong>Date:</strong> {new Date(selectedCase.created_at).toLocaleString()}</p>
                  <p><strong>Session ID:</strong> {selectedCase.session_id}</p>
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <h4>Message Content:</h4>
                  <div style={{ 
                    backgroundColor: '#f8f9fa', 
                    padding: '15px', 
                    borderRadius: '8px',
                    border: '1px solid #e9ecef'
                  }}>
                    {selectedCase.content}
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button style={{ 
                    backgroundColor: '#27ae60', 
                    color: 'white', 
                    border: 'none', 
                    padding: '10px 20px', 
                    borderRadius: '4px', 
                    cursor: 'pointer' 
                  }}>
                    Contact Patient
                  </button>
                  <button style={{ 
                    backgroundColor: '#3498db', 
                    color: 'white', 
                    border: 'none', 
                    padding: '10px 20px', 
                    borderRadius: '4px', 
                    cursor: 'pointer' 
                  }}>
                    View Full Session
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;