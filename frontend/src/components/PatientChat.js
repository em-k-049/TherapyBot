import React, { useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder'; 
import { API_BASE_URL, API_ENDPOINTS, apiCall } from '../config/api';

function PatientChat() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm here to help you today. How are you feeling?", sender: 'ai', time: '10:30 AM' }
  ]);
  const [inputText, setInputText] = useState('');
  const [status, setStatus] = useState('Connected');

  // State to manage loading status
  const [isLoading, setIsLoading] = useState(false);

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
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  // UPDATED: This function is modified to match your final backend
  const handleVoiceStop = async (blobUrl, blob) => {
    setIsLoading(true);
    // The key is 'file' to match your backend router
    const audioFormData = new FormData();
    audioFormData.append('file', blob, 'audio.wav');

    try {
      // 1. Send recorded audio to the correct STT endpoint
      const sttResponse = await fetch('http://localhost:8000/voice/transcribe', {
        method: 'POST',
        body: audioFormData,
        // NOTE: Your endpoint is authenticated. You'll need to add your auth token here.
        // headers: { 'Authorization': `Bearer YOUR_AUTH_TOKEN` },
      });
      if (!sttResponse.ok) throw new Error('Speech-to-text failed');
      
      const sttData = await sttResponse.json();
      const transcript = sttData.transcript;

      // 2. Add the user's transcribed message to the chat
      const userMessage = {
        id: messages.length + 1,
        text: transcript,
        sender: 'user',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, userMessage]);

      // 3. Send the transcript to the correct TTS endpoint
      const aiResponseText = `You said: ${transcript}`; // Placeholder for real AI response
      
      // The TTS endpoint now expects FormData, not JSON
      const ttsFormData = new FormData();
      ttsFormData.append('text', aiResponseText);

      const ttsResponse = await fetch('http://localhost:8000/voice/synthesize', {
        method: 'POST',
        body: ttsFormData,
        // NOTE: Your endpoint is authenticated. You'll need to add your auth token here too.
        // headers: { 'Authorization': `Bearer YOUR_AUTH_TOKEN` },
      });
      if (!ttsResponse.ok) throw new Error('Text-to-speech failed');

      // 4. Add the AI's text response to the chat
      const aiMessage = {
        id: messages.length + 2,
        text: aiResponseText,
        sender: 'ai',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMessage]);

      // 5. Play the audio response from the server
      const audioBlob = await ttsResponse.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();

    } catch (error) {
      console.error('Error in voice flow:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Set up the media recorder hook
  const { status: recordingStatus, startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    onStop: handleVoiceStop,
  });

  const isRecording = recordingStatus === 'recording';

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

      <main className="chat-main">
        <div className="chat-panel">
          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className={`message-bubble ${message.sender}`}>{message.text}</div>
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
            {/* Voice input button */}
            <button 
              className={`btn-voice ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
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
            <button className="btn-send" onClick={sendMessage}>
              Send
            </button>
          </div>

          {/* "Processing..." or "Listening..." message */}
          {(isRecording || isLoading) && (
            <div style={{
              padding: '10px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              marginTop: '10px',
              fontSize: '14px',
              color: isRecording ? '#e74c3c' : '#3498db'
            }}>
              {isRecording ? '🎙️ Listening... Speak now' : '🧠 Processing...'}
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