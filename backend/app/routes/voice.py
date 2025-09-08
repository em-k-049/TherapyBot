from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..models import User
from ..deps import get_db, get_current_user
from ..services.voice import transcribe_audio, synthesize_speech

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transcribe audio file to text"""
    transcript = transcribe_audio(file)
    return {"transcript": transcript}

@router.post("/synthesize")
async def synthesize(
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Convert text to speech audio"""
    audio_data = synthesize_speech(text)
    return Response(
        content=audio_data,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=speech.mp3"}
    )