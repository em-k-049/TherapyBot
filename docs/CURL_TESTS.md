# Curl Test Commands for AI Fallback System

## 1. Test Ollama Directly (WSL)

```bash
# Test Ollama connection
curl -X POST "http://127.0.0.1:11434/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "prompt": "You are a therapist. User: Hello, how are you? Therapist:",
    "stream": false
  }'
```

Expected response:
```json
{
  "model": "llama2",
  "created_at": "2024-01-01T12:00:00Z",
  "response": "Hello! I'm doing well, thank you for asking. How are you feeling today?",
  "done": true
}
```

## 2. Test FastAPI Fallback System

### Test Chat (No Auth)
```bash
curl -X POST "http://localhost:8000/messages/test-chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I am feeling anxious about work"}'
```

### Test Chat (With Auth)
```bash
curl -X POST "http://localhost:8000/messages/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "I need help with stress management"}'
```

Expected response (success):
```json
{
  "user_message": "I am feeling anxious about work",
  "ai_response": "I understand that work-related anxiety can feel overwhelming...",
  "status": "success"
}
```

Expected response (fallback):
```json
{
  "user_message": "I am feeling anxious about work", 
  "ai_response": "I hear that you're feeling anxious about work...",
  "error": "Vertex AI error: timeout",
  "status": "error"
}
```

## 3. Test Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## 4. Troubleshooting Commands

### Check Ollama Status
```bash
# In WSL
ollama list
ollama serve
```

### Check Docker Network (if using Docker)
```bash
# Test from inside container
curl -X POST "http://host.docker.internal:11434/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama2", "prompt": "test", "stream": false}'
```

### Check FastAPI Logs
```bash
# Look for these log messages:
# ✅ Vertex AI response successful
# ❌ Vertex AI failed: [error]
# ✅ Ollama fallback successful
# ❌ Ollama fallback failed: [error]
```