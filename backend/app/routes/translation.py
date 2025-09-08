from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict
from ..models import User
from ..deps import get_current_user
from ..services.translation import translate_text, detect_language, get_supported_languages

router = APIRouter(prefix="/translation", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = None

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str

class LanguageDetectionResponse(BaseModel):
    text: str
    detected_language: str

@router.post("/translate", response_model=TranslationResponse)
def translate(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user)
):
    """Translate text to target language"""
    translated = translate_text(
        request.text, 
        request.target_language, 
        request.source_language
    )
    
    source_lang = request.source_language or detect_language(request.text)
    
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated,
        source_language=source_lang,
        target_language=request.target_language
    )

@router.post("/detect", response_model=LanguageDetectionResponse)
def detect(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """Detect language of text"""
    detected = detect_language(text)
    
    return LanguageDetectionResponse(
        text=text,
        detected_language=detected
    )

@router.get("/languages", response_model=Dict[str, str])
def get_languages():
    """Get supported languages"""
    return get_supported_languages()