from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import base64
from ..schemas import MessageCreate, MessageRead, MessageResponse
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_message: str
    ai_response: str
    ai_audio: Optional[str] = None

class VoiceChatRequest(BaseModel):
    message: str
    return_audio: bool = True
from ..models import Message, Session as SessionModel, User
from ..deps import get_db, get_current_user
from ..services.ai_service import get_ai_service
import logging

logger = logging.getLogger(__name__)
from ..services.risk_assessment import assess_risk, detect_risk
from ..services.voice import transcribe_audio, synthesize_speech
from ..services.translation import translate_text, detect_language
from ..services.guardrails import sanitize_input, validate_response, is_safe_content, get_safety_warning
from ..services.audit import log_message_sent, log_escalation_created
from ..services.metrics import record_message, record_escalation
from ..services.logging import log_escalation_event

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/test-chat")
async def test_chat(request: ChatRequest):
    """Test chat endpoint without authentication"""
    try:
        logger.info(f"Test chat request: {request.message}")
        ai_service = get_ai_service()
        ai_response = await ai_service.get_response(request.message)
        
        return {
            "user_message": request.message,
            "ai_response": ai_response,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Test chat error: {str(e)}")
        return {
            "user_message": request.message,
            "ai_response": "I'm having technical difficulties. Please try again in a moment.",
            "error": str(e),
            "status": "error"
        }

@router.post("/", response_model=MessageResponse)
async def send_message(
    session_id: UUID = Form(...),
    content: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    translate_to: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session exists and belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Handle audio transcription
    message_text = content
    audio_data = None
    
    if audio:
        # Store audio data as base64
        audio_bytes = await audio.read()
        audio_data = base64.b64encode(audio_bytes).decode()
        
        # Transcribe audio if no text provided
        if not message_text:
            message_text = transcribe_audio(audio)
    
    if not message_text:
        raise HTTPException(status_code=400, detail="Either content or audio must be provided")
    
    # Sanitize input for safety and PII protection
    original_message = message_text
    sanitized_message = sanitize_input(message_text)
    safety_warning = get_safety_warning(sanitized_message)
    
    # Check if content is safe to process
    if not is_safe_content(original_message):
        # For crisis situations, still process but with immediate escalation
        risk_analysis = {"is_risky": True, "risk_score": 1.0, "tags": ["crisis:immediate_intervention"]}
    else:
        # Check for risk and escalation using sanitized message
        risk_analysis = detect_risk(sanitized_message)
    
    # Store user message (use sanitized content with encryption)
    user_message = Message(
        session_id=session_id,
        sender_id=current_user.id,
        audio_data=audio_data,
        is_escalated=risk_analysis["is_risky"],
        risk_score=risk_analysis["risk_score"],
        risk_tags=risk_analysis["tags"]
    )
    user_message.set_content(sanitized_message)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Record metrics
    record_message(current_user.role.name)
    
    # Log message sent
    log_message_sent(db, current_user, str(user_message.id), risk_analysis["is_risky"])
    
    # Log escalation if risky
    if risk_analysis["is_risky"]:
        log_escalation_created(db, current_user, str(user_message.id), risk_analysis["risk_score"], risk_analysis["tags"])
        record_escalation(risk_analysis["risk_score"])
        log_escalation_event(str(user_message.id), risk_analysis["risk_score"], str(current_user.id), "escalation_created")
    
    # Trigger escalation task if risky
    if risk_analysis["is_risky"]:
        from .tasks import escalate_case_task
        escalate_case_task.delay(
            str(current_user.id),
            sanitized_message,
            risk_analysis["risk_score"]
        )
    
    # Get AI response using sanitized message
    ai_response_text = await get_ai_response(sanitized_message)
    
    # Validate AI response for safety
    validated_ai_response = validate_response(ai_response_text)
    
    # Add safety warning if needed
    if safety_warning:
        validated_ai_response = f"{safety_warning}\n\n{validated_ai_response}"
    
    # Translate AI response if requested
    translated_ai_response = validated_ai_response
    if translate_to and translate_to != 'en':
        translated_ai_response = translate_text(validated_ai_response, translate_to)
    
    # Synthesize AI response to audio
    ai_audio_bytes = synthesize_speech(translated_ai_response)
    ai_audio_b64 = base64.b64encode(ai_audio_bytes).decode()
    
    # Store AI message
    ai_message = Message(
        session_id=session_id,
        sender_id=current_user.id,  # For simplicity, using same user
        content=ai_response_text,
        is_escalated=False
    )
    db.add(ai_message)
    db.commit()
    
    return MessageResponse(
        message=MessageRead(
            id=user_message.id,
            content=user_message.get_content(),
            created_at=user_message.created_at,
            is_escalated=user_message.is_escalated,
            audio_data=user_message.audio_data,
            risk_score=user_message.risk_score,
            risk_tags=user_message.risk_tags
        ),
        ai_response=translated_ai_response,
        ai_audio=ai_audio_b64
    )

@router.get("/{session_id}", response_model=List[MessageRead])
def get_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session access
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Allow access if user owns session or is consultant/admin
    if (session.user_id != current_user.id and 
        current_user.role.name not in ["consultant", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    return [
        MessageRead(
            id=msg.id,
            content=msg.get_content(),
            created_at=msg.created_at,
            is_escalated=msg.is_escalated,
            audio_data=msg.audio_data,
            risk_score=msg.risk_score,
            risk_tags=msg.risk_tags
        )
        for msg in messages
    ]

@router.post("/chat")
async def simple_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat endpoint with Vertex AI + Ollama fallback"""
    try:
        logger.info(f"Chat request: {request.message}")
        ai_service = get_ai_service()
        ai_response = await ai_service.get_response(request.message)
        
        return {
            "user_message": request.message,
            "ai_response": ai_response
        }
    except Exception as e:
        logger.error(f"AI services error: {str(e)}")
        return {
            "user_message": request.message,
            "ai_response": "I'm sorry, I'm having technical difficulties right now. Please try again in a moment.",
            "error": str(e)
        }

@router.post("/voice-chat")
async def voice_chat(
    request: VoiceChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Voice-first chat endpoint with TTS response"""
    try:
        if not request.message:
            raise HTTPException(status_code=422, detail={"error": "Message is required", "field": "message"})
            
        # Get AI response
        ai_service = get_ai_service()
        ai_response = await ai_service.get_response(request.message)
        
        return {
            "ai_response": ai_response,
            "user_message": request.message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        return {
            "user_message": request.message or "",
            "ai_response": "I'm having technical difficulties. Please try again in a moment.",
            "error": str(e)
        }

@router.post("/chat/voice")
async def chat_voice(
    message: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Voice chat endpoint with Vertex AI + Ollama fallback"""
    try:
        # Handle audio transcription if audio provided
        if audio and not message:
            message = transcribe_audio(audio)
        
        if not message:
            return {"error": "Either message or audio must be provided"}
        
        # Get AI response (Vertex AI with Ollama fallback)
        ai_response = await get_ai_response(message)
        
        return {
            "reply": ai_response,
            "transcribed_text": message if audio else None
        }
    except Exception as e:
        logger.error(f"All AI services failed: {e}")
        return {
            "error": "No AI backend available",
            "transcribed_text": message if audio else None
        }