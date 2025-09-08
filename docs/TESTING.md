# TherapyBot Testing Guide

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Backend Tests Only
```bash
cd backend
pytest test_endpoints.py -v
```

### Frontend Tests Only
```bash
cd frontend
npm install
npx playwright install
npm run test
```

## Test Coverage

### Backend Tests (`backend/test_endpoints.py`)
- ✅ `/messages/test-chat` - Success, failure, invalid payload
- ✅ `/messages/chat` - Success, auth required, AI failure
- ✅ `/messages/voice-chat` - Success, missing message, error handling
- ✅ `/health` - Health check endpoint
- ✅ Error handling - Malformed JSON, missing content type

### Frontend Tests (`frontend/tests/chat.spec.js`)
- ✅ Text message sending and AI response
- ✅ Voice input with speech recognition mock
- ✅ API error handling with user-friendly messages
- ✅ Voice not supported scenarios
- ✅ UI status and privacy indicators

## Browser Support
Tests run on:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari/WebKit

## Test Commands

### Backend
```bash
# Run all tests
pytest

# Run specific test
pytest test_endpoints.py::TestChatEndpoints::test_chat_success -v

# Run with coverage
pytest --cov=app test_endpoints.py
```

### Frontend
```bash
# Run all tests
npm run test

# Run in headed mode (see browser)
npm run test-headed

# Debug mode
npm run test-debug

# Specific browser
npx playwright test --project=chromium
```

## Debugging Failed Tests

### Backend Issues
1. Check if FastAPI server is running
2. Verify AI services (Vertex AI/Ollama) are configured
3. Check database connections
4. Review logs for authentication issues

### Frontend Issues
1. Ensure React app is running on localhost:3000
2. Check browser console for JavaScript errors
3. Verify API endpoints are responding
4. Test speech recognition in actual browser

## Mock Data

### API Responses
Tests use mocked AI responses:
```json
{
  "user_message": "Hello",
  "ai_response": "Hello! I'm here to help you today. How are you feeling?"
}
```

### Speech Recognition
Frontend tests mock `SpeechRecognition` API:
```javascript
window.SpeechRecognition = class MockSpeechRecognition {
  // Mock implementation
}
```

## Continuous Integration

Add to your CI pipeline:
```yaml
- name: Run Backend Tests
  run: cd backend && pytest test_endpoints.py

- name: Run Frontend Tests  
  run: cd frontend && npm ci && npx playwright install && npm run test
```