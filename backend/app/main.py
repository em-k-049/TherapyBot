from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, messages, escalation, voice, notifications, translation, guardrails, analytics, wellness, admin, privacy, health, chat
from .models import Base
from .db import engine
from .middleware import AuditMiddleware
from .services.metrics import get_metrics
from .startup_checks import run_startup_checks
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from .schemas import TTSRequest
from .routes import voice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TherapyBot API")

# Run startup checks
@app.on_event("startup")
async def startup_event():
    logger.info("Starting TherapyBot API...")
    run_startup_checks()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# TTS-STT endpoint
# In main.py, after your app is defined

@app.post("/messages/stt")
async def speech_to_text_endpoint(audio_file: UploadFile = File(...)):
    try:
        transcript = voice_service.transcribe_audio(audio_file)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")


@app.post("/messages/tts")
async def text_to_speech_endpoint(request: TTSRequest):
    try:
        audio_bytes = voice_service.synthesize_speech(request.text)
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate audio.")

        # Return the raw MP3 audio data with the correct media type
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during TTS conversion: {str(e)}")


# Add audit logging middleware
#app.add_middleware(AuditMiddleware)

# Add metrics endpoint
@app.get("/metrics")
def metrics():
    return get_metrics()

# Add health endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TherapyBot API"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(escalation.router)
app.include_router(voice.router)
app.include_router(notifications.router)
app.include_router(translation.router)
app.include_router(guardrails.router)
app.include_router(analytics.router)
app.include_router(wellness.router)
app.include_router(admin.router)
app.include_router(privacy.router)
app.include_router(health.router)
app.include_router(chat.router)