# AI Integration Setup Guide

## Environment Configuration

To enable real AI responses from Google Vertex AI, ensure these environment variables are set in your `.env` file:

```bash
# Google Cloud Vertex AI Configuration
GCP_PROJECT_ID=therapybot-469702
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-credentials.json

# Vertex AI Model Configuration
VERTEX_AI_MODEL=gemini-2.0-flash
VERTEX_AI_TEMPERATURE=0.7
VERTEX_AI_MAX_TOKENS=1024
```

## Required Files

1. **GCP Service Account Key**: Place your Google Cloud service account JSON file at:
   - Local development: `./secrets/gcp-credentials.json`
   - Docker: `/app/secrets/gcp-credentials.json`

2. **Environment Variables**: Update your `.env` file with the values above.

## API Endpoints

### Text Chat
**Endpoint**: `POST /messages/chat`

**Request**:
```json
{
  "message": "Hello, I feel anxious today"
}
```

**Response**:
```json
{
  "user_message": "Hello, I feel anxious today",
  "ai_response": "I understand you're feeling anxious. That's a very common experience, and I'm here to help you work through it. Can you tell me more about what might be contributing to your anxiety today?"
}
```

### Voice Chat
**Endpoint**: `POST /messages/voice-chat`

**Request**:
```json
{
  "message": "I feel anxious today",
  "return_audio": true
}
```

**Response**:
```json
{
  "user_message": "I feel anxious today",
  "ai_response": "I hear that you're feeling anxious. It takes courage to reach out when you're struggling. What's been on your mind that might be contributing to these feelings?",
  "ai_audio": "base64-encoded-audio-data"
}
```

## Testing

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response should include:
```json
{
  "status": "healthy",
  "database": "connected",
  "vertex_ai": "connected"
}
```

### 2. Test AI Endpoints
```bash
python test_ai_endpoints.py
```

### 3. Frontend Testing
1. Open the patient dashboard
2. Try both text and voice chat
3. Verify you receive real AI responses, not placeholders

## Troubleshooting

### Issue: "Vertex AI not available"
- Check if `google-cloud-aiplatform` is installed: `pip install google-cloud-aiplatform`
- Verify credentials file exists and is valid
- Check GCP project ID and region are correct

### Issue: "Fallback responses only"
- Verify environment variables are loaded correctly
- Check application logs for Vertex AI initialization errors
- Ensure GCP service account has proper permissions

### Issue: "Authentication failed"
- Verify service account key is valid and not expired
- Check if Vertex AI API is enabled in your GCP project
- Ensure service account has `Vertex AI User` role

## Expected Behavior

✅ **Working correctly**:
- Real therapeutic responses from Gemini model
- Contextual and empathetic replies
- Responses are 2-3 sentences for good conversation flow

❌ **Not working**:
- Generic placeholder responses like "This is a placeholder reply"
- Short, non-contextual responses
- Error messages about AI unavailability

## Frontend Integration

The frontend automatically uses the correct endpoints:
- **Text chat**: Uses `/messages/chat` endpoint
- **Voice chat**: Uses `/messages/voice-chat` endpoint with TTS support

Both endpoints return real AI responses when properly configured.