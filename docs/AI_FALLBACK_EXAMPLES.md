# AI Fallback Examples

## Request/Response Flows

### 1. Successful Vertex AI Response

**Request:**
```bash
curl -X POST "http://localhost:8000/chat/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "I am feeling anxious about work"}'
```

**Response (Vertex AI working):**
```json
{
  "reply": "I understand that work-related anxiety can feel overwhelming. It's completely normal to experience these feelings, especially when facing challenging situations. Would you like to explore some specific coping strategies that might help you manage these anxious thoughts?"
}
```

### 2. Vertex AI Down → Ollama Fallback

**Request:**
```bash
curl -X POST "http://localhost:8000/chat/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "I need help with stress management"}'
```

**Response (Vertex AI failed, Ollama working):**
```json
{
  "reply": "I hear that you're looking for help with stress management. Stress is something many people struggle with, and it's great that you're reaching out. Some effective techniques include deep breathing exercises, regular physical activity, and setting healthy boundaries."
}
```

### 3. Both Services Down → Error Response

**Request:**
```bash
curl -X POST "http://localhost:8000/chat/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "How can I improve my mental health?"}'
```

**Response (Both services failed):**
```json
{
  "error": "No AI backend available"
}
```

### 4. Voice Chat with Fallback

**Request:**
```bash
curl -X POST "http://localhost:8000/chat/voice" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "message=I'm having trouble sleeping"
```

**Response (Vertex AI working):**
```json
{
  "reply": "Sleep difficulties can be really challenging and affect many aspects of your well-being. There are several approaches we can explore together, such as establishing a consistent bedtime routine, creating a calm sleep environment, and addressing any underlying worries that might be keeping you awake.",
  "transcribed_text": null
}
```

**Response (Vertex AI down, Ollama working):**
```json
{
  "reply": "Sleep problems are very common and can be quite distressing. Let's work together to identify what might be contributing to your sleep difficulties. Some helpful strategies include maintaining regular sleep hours, avoiding screens before bed, and practicing relaxation techniques.",
  "transcribed_text": null
}
```

## Configuration Examples

### Environment Variables (.env)

```env
# Vertex AI Configuration
USE_VERTEX_AI=true
GCP_PROJECT_ID=therapybot-469702
GCP_REGION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash
VERTEX_AI_TEMPERATURE=0.7
VERTEX_AI_MAX_TOKENS=1024

# Ollama Configuration (Fallback)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Testing Different Scenarios

1. **Normal Operation (Vertex AI working):**
   - Set `USE_VERTEX_AI=true`
   - Ensure GCP credentials are valid
   - Vertex AI responses will be used

2. **Force Ollama Usage:**
   - Set `USE_VERTEX_AI=false`
   - All requests will go directly to Ollama

3. **Test Fallback:**
   - Set `USE_VERTEX_AI=true`
   - Stop GCP credentials or cause Vertex AI to fail
   - Requests will automatically fallback to Ollama

4. **Test Error Handling:**
   - Set `USE_VERTEX_AI=true`
   - Stop both Vertex AI and Ollama
   - Should return error response

## Frontend Integration

The frontend doesn't need changes - it will always receive a `reply` field:

```javascript
// Frontend code remains the same
const response = await fetch('/chat/text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ message: userInput })
});

const data = await response.json();

if (data.reply) {
  // Display AI response (from either Vertex AI or Ollama)
  displayMessage(data.reply);
} else if (data.error) {
  // Handle error case
  displayError(data.error);
}
```

## Monitoring and Logs

The system logs which AI service is being used:

```
INFO: Successfully got Vertex AI response
INFO: Vertex AI failed: timeout, trying Ollama fallback  
INFO: Successfully got Ollama fallback response
ERROR: Both Vertex AI and Ollama failed
```