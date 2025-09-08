import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL, API_ENDPOINTS, apiCall } from '../config/api';

function PatientChat() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm here to help you today. How are you feeling?", sender: 'ai', time: '10:30 AM' }
  ]);
  const [inputText, setInputText] = useState('');
  const [status, setStatus] = useState('Connected');
  const [speechSupported, setSpeechSupported] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check speech recognition support
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechSupported(!!window.SpeechRecognition);
  }, []);

  const sendMessage = async () => {
    if (!inputText.trim()) return;
    
    const userMessage = {
      id: messages.length + 1,
      text: inputText,
      sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);
    const messageText = inputText;
    setInputText('');
    
    try {
      const data = await apiCall(API_ENDPOINTS.CHAT, {
        method: 'POST',
        body: JSON.stringify({ message: messageText })
      });
      
      const aiMessage = {
        id: messages.length + 2,
        text: data.ai_response,
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: "I'm sorry, I'm having trouble connecting right now. Please try again.",
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const startVoiceRecording = () => {
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
        setIsRecording(true);
        setTranscript('');
      };
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          }
        }
        
        if (finalTranscript) {
          setInputText(finalTranscript);
          setTranscript(finalTranscript);
          // Clear input and auto-send voice input
          setInputText(finalTranscript);
          setTimeout(() => {
            sendVoiceMessage(finalTranscript);
          }, 500);
        }
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please allow microphone access and try again.');
        } else {
          alert('Speech recognition failed. Please try again.');
        }
      };
      
      recognition.onend = () => {
        setIsRecording(false);
      };
      
      recognitionRef.current = recognition;
      recognition.start();
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      alert('Failed to start voice recognition');
    }
  };

  const stopVoiceRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  };

  const sendVoiceMessage = async (messageText) => {
    const userMessage = {
      id: messages.length + 1,
      text: messageText,
      sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const data = await apiCall(API_ENDPOINTS.VOICE_CHAT, {
        method: 'POST',
        body: JSON.stringify({ message: messageText, return_audio: true })
      });
      
      const aiMessage = {
        id: messages.length + 2,
        text: data.ai_response,
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Speak the AI response
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(data.ai_response);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;
        speechSynthesis.speak(utterance);
      }
    } catch (error) {
      console.error('Error sending voice message:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: "I'm sorry, I'm having trouble connecting right now. Please try again.",
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="patient-chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="logo">
          <h2>🌲 TherapyBot</h2>
        </div>
        <div className="user-info">
          <span>Welcome, Patient</span>
        </div>
      </header>

      {/* Main Chat Panel */}
      <main className="chat-main">
        <div className="chat-panel">
          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className={`message-bubble ${message.sender}`}>
                  {message.text}
                </div>
                <div className="message-time">{message.time}</div>
              </div>
            ))}
          </div>
          
          <div className="chat-input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
            />
            {speechSupported ? (
              <button 
                className={`btn-voice ${isRecording ? 'recording' : ''}`}
                onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                title={isRecording ? 'Stop Recording' : 'Start Voice Input'}
                style={{
                  backgroundColor: isRecording ? '#e74c3c' : '#3498db',
                  color: 'white',
                  border: 'none',
                  padding: '10px',
                  borderRadius: '4px',
                  marginRight: '5px',
                  cursor: 'pointer'
                }}
              >
                {isRecording ? '⏹️' : '🎤'}
              </button>
            ) : (
              <button 
                disabled
                title="Voice input not supported in this browser"
                style={{
                  backgroundColor: '#95a5a6',
                  color: 'white',
                  border: 'none',
                  padding: '10px',
                  borderRadius: '4px',
                  marginRight: '5px',
                  cursor: 'not-allowed'
                }}
              >
                🚫
              </button>
            )}
            <button className="btn-send" onClick={sendMessage}>
              Send
            </button>
          </div>
          {isRecording && (
            <div style={{
              padding: '10px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              marginTop: '10px',
              fontSize: '14px',
              color: '#e74c3c'
            }}>
              🎙️ Listening... Speak now
            </div>
          )}
          {!speechSupported && (
            <div style={{
              padding: '10px',
              backgroundColor: '#fff3cd',
              borderRadius: '4px',
              marginTop: '10px',
              fontSize: '12px',
              color: '#856404',
              textAlign: 'center'
            }}>
              Voice input not supported. Please use Chrome or Edge for voice features.
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="chat-footer">
        <div className="status-info">
          <span className="status">Status: {status}</span>
          <span className="privacy">🔒 Your conversation is private and secure</span>
        </div>
      </footer>
    </div>
  );
}

export default PatientChat;