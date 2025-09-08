from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from ..models import User
from ..deps import get_db, get_current_user
from ..services.vertex_ai import get_ai_response
from ..services.voice import transcribe_audio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class TextChatRequest(BaseModel):
    message: str

class VoiceChatRequest(BaseModel):
    message: Optional[str] = None
    return_audio: bool = True

class ChatResponse(BaseModel):
    reply: str

class VoiceChatResponse(BaseModel):
    ai_response: str
    transcribed_text: Optional[str] = None

@router.post("/text", response_model=ChatResponse)
async def chat_text(
    request: TextChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Text chat endpoint with Vertex AI + Ollama fallback"""
    try:
        ai_response = await get_ai_response(request.message)
        return ChatResponse(reply=ai_response)
    except Exception as e:
        logger.error(f"All AI services failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"error": "No AI backend available"}
        )

@router.post("/voice")
async def chat_voice_json(
    request: VoiceChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Voice chat endpoint with JSON input"""
    try:
        logger.info(f"Voice chat request: message='{request.message}', return_audio={request.return_audio}")
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        ai_response = await get_ai_response(request.message)
        
        return {
            "ai_response": ai_response,
            "transcribed_text": None
        }
    except Exception as e:
        logger.error(f"All AI services failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="No AI backend available"
        )

@router.post("/voice/upload")
async def chat_voice_upload(
    message: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Voice chat endpoint with file upload"""
    try:
        # Handle audio transcription if audio provided
        if audio and not message:
            message = transcribe_audio(audio)
        
        if not message:
            return {"error": "Either message or audio must be provided"}
        
        ai_response = await get_ai_response(message)
        
        return {
            "ai_response": ai_response,
            "transcribed_text": message if audio else None
        }
    except Exception as e:
        logger.error(f"All AI services failed: {e}")
        return {
            "error": "No AI backend available",
            "transcribed_text": message if audio else None
        }