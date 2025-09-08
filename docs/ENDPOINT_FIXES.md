# AI Chat Endpoint Fixes

## Problem Identified
The backend was already working correctly with real Vertex AI integration, but the frontend PatientChat component was using hardcoded placeholder responses instead of calling the backend API endpoints.

## Changes Made

### 1. Frontend PatientChat Component (`frontend/src/components/PatientChat.js`)

**Before**: Used hardcoded responses
```javascript
// Simulate AI response
setTimeout(() => {
  const aiResponse = {
    id: messages.length + 2,
    text: "Thank you for sharing. I'm here to listen and support you.",
    sender: 'ai',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
  setMessages(prev => [...prev, aiResponse]);
}, 1000);
```

**After**: Calls real backend API
```javascript
const response = await fetch(`${API_URL}/messages/chat`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: messageText })
});

const data = await response.json();
const aiMessage = {
  id: messages.length + 2,
  text: data.ai_response,  // Real AI response
  sender: 'ai',
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
};
```

### 2. Added Voice Chat Integration
- Added `sendVoiceMessage()` function that calls `/messages/voice-chat` endpoint
- Integrated Text-to-Speech for AI responses in voice mode
- Auto-sends voice input after speech recognition completes

## Backend Endpoints (Already Working)

### Text Chat
- **Endpoint**: `POST /messages/chat`
- **Request**: `{ "message": "Hello, I feel anxious today" }`
- **Response**: `{ "user_message": "...", "ai_response": "Real AI response from Vertex AI" }`

### Voice Chat  
- **Endpoint**: `POST /messages/voice-chat`
- **Request**: `{ "message": "I feel anxious", "return_audio": true }`
- **Response**: `{ "user_message": "...", "ai_response": "Real AI response", "ai_audio": "base64-audio" }`

## Verification

### Backend Test
```bash
python test_ai_simple.py
```
Expected: Real AI responses from Vertex AI (not placeholders)

### Frontend Test
1. Open patient dashboard or PatientChat component
2. Send text message: "Hello, I feel anxious today"
3. Expected: Real therapeutic AI response, not "Thank you for sharing..."
4. Try voice input (Chrome/Edge only)
5. Expected: AI response spoken back via TTS

## Environment Requirements

Ensure these are set in `.env`:
```bash
GCP_PROJECT_ID=therapybot-469702
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-credentials.json
VERTEX_AI_MODEL=gemini-2.0-flash
```

## Result
- ✅ Text chat now returns real AI responses
- ✅ Voice chat now returns real AI responses with TTS
- ✅ No more placeholder responses
- ✅ Proper error handling for API failures