# Manual Testing Guide

## Quick Setup & Test

### 1. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Test Backend Endpoints
```bash
# In new terminal
cd backend
python test_simple.py
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm start
```

### 4. Test Frontend Manually
1. Open http://localhost:3000/chat
2. Type "Hello, how are you?" and click Send
3. Verify AI response appears
4. Click microphone button (if supported)
5. Speak "I need help" and verify response

## Expected Results

### Backend Tests
```
🏥 Testing Health Endpoint
Status: 200
✅ Health check passed: {'status': 'healthy', 'service': 'TherapyBot API'}

💬 Testing Chat Endpoint  
Status: 200
✅ Chat test passed
Response: I understand you're feeling...

🚫 Testing Invalid Payload
Status: 422
✅ Invalid payload correctly rejected

📊 Test Results
Passed: 3/3
🎉 All tests passed!
```

### Frontend Manual Tests
- ✅ Text message sends and receives AI response
- ✅ Voice button shows (if browser supports speech recognition)
- ✅ Error messages display when backend is down
- ✅ UI is responsive and user-friendly

## Troubleshooting

### Backend Issues
- **Port 8000 in use**: Kill process or use different port
- **AI services failing**: Check Vertex AI credentials or Ollama setup
- **Database errors**: Ensure PostgreSQL is running

### Frontend Issues  
- **Port 3000 in use**: React will offer alternative port
- **API calls failing**: Check backend is running on port 8000
- **Voice not working**: Use Chrome/Edge, allow microphone access

## API Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat Test
```bash
curl -X POST http://localhost:8000/messages/test-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Expected Response
```json
{
  "user_message": "Hello",
  "ai_response": "Hello! I'm here to help you today. How are you feeling?",
  "status": "success"
}
```